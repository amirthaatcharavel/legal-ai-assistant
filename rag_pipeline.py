from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

import os




DATA_PATH = "data/"
DB_PATH = "vectorstore/"

# =========================
# 🔐 EMBEDDINGS (LOAD ONCE)
# =========================
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
    return _embeddings


# =========================
# 🔥 CREATE VECTOR DB (PDFs)
# =========================
def create_vector_db():
    documents = []

    # 🔥 Ensure folder exists
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    for file in os.listdir(DATA_PATH):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DATA_PATH, file))
            documents.extend(loader.load())

    # ⚠️ Handle empty case
    if not documents:
        print("⚠️ No PDFs found. Creating empty DB...")
        db = FAISS.from_texts(
            ["Initial empty legal document"],
            get_embeddings()
        )
        db.save_local(DB_PATH)
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    docs = splitter.split_documents(documents)

    db = FAISS.from_documents(docs, get_embeddings())
    db.save_local(DB_PATH)

    print("✅ Vector DB created from PDFs!")


# =========================
# 🔥 LOAD DB (SAFE)
# =========================
def load_db():
    index_file = os.path.join(DB_PATH, "index.faiss")

    if not os.path.exists(index_file):
        print("⚠️ FAISS DB not found. Creating new DB...")
        create_vector_db()

    return FAISS.load_local(
        DB_PATH,
        get_embeddings(),
        allow_dangerous_deserialization=True
    )


# =========================
# 🔥 ADD CASES TO DB
# =========================
def add_cases_to_db(cases):

    db = load_db()

    # 🔥 Track existing titles
    existing_titles = set()

    try:
        for doc in db.docstore._dict.values():
            title = doc.metadata.get("title")
            if title:
                existing_titles.add(title.lower())
    except:
        pass

    new_docs = []

    for case in cases:
        try:
            title = case.get("title", "").strip()
            link = case.get("link", "")

            normalized = re.sub(r'\W+', '', title.lower())

            if not title or any(
                normalized == re.sub(r'\W+', '', t)
                for t in existing_titles):
                    print(f"⏩ Skipping duplicate: {title}")
                    continue

            print(f"📥 Fetching: {title}")

            text = re.sub(r'\s+', ' ', text)   # clean spacing
            text = text.strip()

            if not text or len(text.strip()) < 100:
                continue

            text = text[:20000]

            new_docs.append(
                Document(
                    page_content=text,
                    metadata={
                        "title": title,
                        "source": "Indian Kanoon",
                        "link": link
                    }
                )
            )

        except Exception as e:
            print("❌ Error adding case:", e)

    if not new_docs:
        print("⚠️ No new documents to add.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    split_docs = splitter.split_documents(new_docs)

    db.add_documents(split_docs)
    db.save_local(DB_PATH)

    print(f"✅ Added {len(split_docs)} chunks to DB")


# =========================
# 🔍 RETRIEVE CONTEXT
# =========================
def is_specific_case_query(query):
    keywords = ["vs", "v.", "versus"]
    return any(k in query.lower() for k in keywords)


def retrieve_context(query, k=8):
    db = load_db()

    # 🔍 Step 1: get more candidates (important)
    docs = db.similarity_search(query, k=30)
    # 🔥 exact case priority
    for d in docs:
        title = d.metadata.get("title", "").lower()
        if query_lower in title:
            return f"Case: {d.metadata.get('title')}\n{d.page_content[:12000]}"

    if not docs:
        return ""

    query_lower = query.lower()

    # =========================
    # 🔥 STEP 2: SMART CASE DETECTION
    # =========================
    stopwords = {"vs", "v", "case", "of", "the", "and"}
    query_words = [w for w in query_lower.split() if w not in stopwords]

    scored_docs = []

    for d in docs:
        title = d.metadata.get("title", "").lower()
        text = d.page_content.lower()

        # 🔥 word overlap score
        overlap = sum(1 for w in query_words if w in title or w in text)

        # 🔥 exact phrase boost
        exact_match = query_lower in title

        score = overlap + (3 if exact_match else 0)

        scored_docs.append((score, d))

    # =========================
    # 🔥 STEP 3: SORT BEST MATCHES
    # =========================
    scored_docs.sort(reverse=True, key=lambda x: x[0])

    # keep only strong docs
    best_docs = [d for score, d in scored_docs if score >= 1]

    # fallback if weak
    if not best_docs:
        print("⚠️ No strong match, using raw docs")
        best_docs = [d for _, d in scored_docs[:5]]

    # =========================
    # 🔥 STEP 4: DOMINANT CASE LOGIC
    # =========================
    title_count = {}

    for d in best_docs:
        title = d.metadata.get("title", "")
        title_count[title] = title_count.get(title, 0) + 1

    main_case = max(title_count, key=title_count.get)

    # keep only that case
    filtered_docs = [
        d for d in best_docs
        if d.metadata.get("title") == main_case
    ]

    # fallback (important)
    if not filtered_docs:
        filtered_docs = best_docs[:5]

    # =========================
    # 🔥 STEP 5: SORT BEST CHUNKS
    # =========================
    filtered_docs = sorted(
        filtered_docs,
        key=lambda x: len(x.page_content),
        reverse=True
    )[:k]

    # =========================
    # 🔥 STEP 6: BUILD CONTEXT
    # =========================
    context = "\n\n".join([
        f"Case: {d.metadata.get('title','')}\n{d.page_content}"
        for d in filtered_docs
    ])
    context = context[:12000]

    return context


# =========================
# 🔍 RETRIEVE WITH SCORES
# =========================
def retrieve_with_scores(query, k=5):
    db = load_db()

    docs_and_scores = db.similarity_search_with_score(query, k=k)

    results = []

    for doc, score in docs_and_scores:
        results.append({
            "content": doc.page_content,
            "title": doc.metadata.get("title", ""),
            "score": score
        })

    return results


# =========================
# 🧹 CLEAR DB
# =========================
def clear_db():
    if os.path.exists(DB_PATH):
        import shutil
        shutil.rmtree(DB_PATH)
        print("🧹 Vector DB cleared.")


# =========================
# 🚀 TEST
# =========================
if __name__ == "__main__":
    create_vector_db()

    # Test retrieval
    # context = retrieve_context("right to privacy india")
    # print(context)