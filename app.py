from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import re
import os

from dotenv import load_dotenv
from groq import Groq

# 🔥 Firebase
import firebase_admin
from firebase_admin import credentials, firestore

# 🔥 Your modules
from data.constitution import ARTICLES
from tools.summarizer import summarize, summarize_text, extract_text
from tools.comparator import compare
from tools.legal_api import fetch_case_context
from rag_pipeline import add_cases_to_db, retrieve_context
from tools.legal_api import extract_case_data
from tools.legal_api import (
    fetch_cases,
    fetch_from_indian_kanoon
)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# =========================
# 🔐 ENV SETUP
# =========================
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# 🔥 FIREBASE INIT
# =========================
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# =========================
# 🚀 FASTAPI INIT
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from bs4 import BeautifulSoup
import re
import requests
tool_definitions = [
    {
        "name": "summarize",
        "description": "Summarize a legal case or document"
    },
    {
        "name": "compare",
        "description": "Compare two legal cases or document with case"
    },
    {
        "name": "fetch",
        "description": "Fetch legal cases from Indian Kanoon"
    }
]
def decide_tool(query):
    prompt = f"""
You are an AI assistant.

Decide which tool to use.

Return ONLY one word:
summarize OR compare OR fetch

Query:
{query}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        tool = completion.choices[0].message.content.strip().lower()

        if tool not in ["summarize", "compare", "fetch"]:
            return "fetch"

        return tool

    except:
        return "fetch"

def select_best_case(query, cases):
    import re

    query = query.lower()

    # 🔥 remove noise words
    stopwords = {"vs", "v", "case", "of", "the", "and"}
    q_words = [w for w in re.findall(r'\w+', query) if w not in stopwords]

    # 🔥 landmark cases (VERY IMPORTANT)
    important_cases = [
        "kesavananda bharati",
        "maneka gandhi",
        "minerva mills",
        "puttaswamy",
        "a.k gopalan",
        "indra sawhney",
        "m nagaraj",
        "shreya singhal"
    ]

    # =========================
    # 🔥 STEP 1: EXACT MATCH (BEST)
    # =========================
    for c in cases:
        title = c.get("title", "").lower()

        if query in title:
            return [c]

    # =========================
    # 🔥 STEP 2: LANDMARK BOOST
    # =========================
    for c in cases:
        title = c.get("title", "").lower()

        for imp in important_cases:
            if imp in query and imp in title:
                return [c]

    # =========================
    # 🔥 STEP 3: BEST SCORE MATCH
    # =========================
    best_case = None
    best_score = 0

    for c in cases:
        title = c.get("title", "").lower()

        title_words = set(re.findall(r'\w+', title))

        score = 0

        # 🔥 word overlap
        for w in q_words:
            if w in title_words:
                score += 2   # weight

        # 🔥 bonus for phrase presence
        if any(w in title for w in q_words):
            score += 1

        if score > best_score:
            best_score = score
            best_case = c

    # =========================
    # 🔥 STEP 4: FALLBACK
    # =========================
    if best_case:
        return [best_case]

    # 🔥 last fallback (first result)
    return [cases[0]] if cases else []

    
def parse_indiankanoon(html):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for i, item in enumerate(soup.select(".result")):

        # 🔥 LIMIT RESULTS
        

        a = item.find("a")
        if not a:
            continue

        # ✅ CLEAN TITLE
        title = a.get_text(" ", strip=True)
        title = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', title)

        link = "https://indiankanoon.org" + a["href"]

        # 🔥 GET SNIPPET
        snippet_tag = item.find(class_="result_snippet")
        snippet = snippet_tag.get_text(" ", strip=True) if snippet_tag else item.get_text(" ", strip=True)

        text = (title + " " + snippet).lower()

        # =========================
        # 📅 YEAR
        # =========================
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        year = year_match.group() if year_match else ""

        # =========================
        # ⚖️ COURT (EXACT NAME)
        # =========================
        court = "Unknown Court"

        courts_map = [
            "Supreme Court of India",
            "Madras High Court",
            "Delhi High Court",
            "Bombay High Court",
            "Calcutta High Court",
            "Karnataka High Court",
            "Kerala High Court",
            "Gujarat High Court",
            "Allahabad High Court",
            "Rajasthan High Court",
            "Punjab and Haryana High Court",
            "Patna High Court",
            "Orissa High Court",
            "Jharkhand High Court",
            "Chhattisgarh High Court",
            "Uttarakhand High Court",
            "Himachal Pradesh High Court",
            "Jammu and Kashmir High Court",
            "Telangana High Court",
            "Andhra Pradesh High Court"
        ]

        for c in courts_map:
            if c.lower() in text:
                court = c
                break

        # 🔥 fallback (if exact not found)
        if court == "Unknown Court":
            if "supreme court" in text:
                court = "Supreme Court of India"
            elif "high court" in text:
                court = "High Court"

        # =========================
        # 📜 CITATION
        # =========================
        citation = ""

        patterns = [
            r'AIR\s*\d{4}\s*[A-Z]+\s*\d+',
            r'\d{4}\s*\d+\s*SCC\s*\d+',
            r'\(\d{4}.*?\)'
        ]

        for p in patterns:
            match = re.search(p, text)
            if match:
                citation = match.group()
                break
        if not citation:
            citation = "Not Available"

        results.append({
            "title": title,
            "link": link,
            "citation": citation,
            "court": court,
            "year": year
        })

    return results

# =========================
# 📦 REQUEST MODELS
# =========================
class AskRequest(BaseModel):
    question: str
    user_id: Optional[str] = "guest"
    filters: Optional[dict] = {}

class LinkRequest(BaseModel):
    link: str

# =========================
# 🔥 CACHE
# =========================
def get_cached(user_id, query):
    doc_id = f"{user_id}_{query}"
    doc = db.collection("legal_cache").document(doc_id).get()
    return doc.to_dict() if doc.exists else None

def save_cache(user_id, query, result, tool):
    doc_id = f"{user_id}_{query}"
    db.collection("legal_cache").document(doc_id).set({
        "user_id": user_id,
        "query": query,
        "result": result,
        "tool": tool
    })

# =========================
# 📜 ARTICLE HANDLER
# =========================
def handle_article_query(query: str):
    match = re.search(r"article\s*(\d+[a-z]?)", query.lower())

    if match:
        key = f"article {match.group(1)}"

        if key in ARTICLES:
            art = ARTICLES[key]
            points_text = "\n• ".join(art["points"])

            return f"""
{key.upper()}

Title: {art['title']}

Explanation:
{art['content']}

Key Points:
• {points_text}
"""
        else:
            return f"⚠️ {key.upper()} not found."

    return None



# =========================
# 🔍 HELPERS
# =========================
def clean_case_name(name):
    return re.sub(r"(case|vs|versus|compare)", "", name).strip()

def extract_case(query: str):
    return re.sub(r"(summarize|explain|case)", "", query.lower()).strip()

def clean_llm_output(text):
    import re

    # remove markdown stars
    text = re.sub(r'\*\*+', '', text)

    # remove extra blank lines
    text = re.sub(r'\n\s*\n', '\n\n', text)

    return text.strip()

    
def rewrite_query(user_query):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Extract the exact legal case name or main legal topic from the query. Return ONLY a short clean search query."
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ]
        )

        refined = completion.choices[0].message.content.strip()

        # 🔥 CLEANING
        refined = refined.replace('"', '').replace("'", "")
        refined = re.sub(r'[^\w\s.v]', '', refined)
        return refined

    except Exception as e:
        print("Query rewrite error:", e)
        return user_query

@app.post("/ask")
async def ask(request: AskRequest):
    # =========================
    # 🧠 MCP-LITE TOOLS
    # =========================

    def summarize_tool(context):
        return summarize_text(context)


    def compare_tool(context, cases):
        prompt = f"""
    You are a legal expert.

    Compare the two cases strictly using ONLY the given context.

    Context:
    {context}

    STRICT FORMAT:

    Case 1: {cases[0]['title']}
    Case 2: {cases[1]['title']}

    Facts:
    - ...

    Issue:
    - ...

    Similarities:
    - ...

    Differences:
    - ...

    Judgment:
    - ...
    """

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        return clean_llm_output(completion.choices[0].message.content)


    # 🔥 TOOL REGISTRY
    tools = {
        "summarize": summarize_tool,
        "compare": compare_tool
    }
    context = ""
    user_id = request.user_id or "guest"
    has_uploaded_doc = user_id in uploaded_text_store

    original_query = request.question.strip()
    query = original_query

    # 🔥 CLEAN QUERY FOR SUMMARY
    q_lower = original_query.lower()
    if any(word in q_lower for word in ["summarize", "summary", "explain"]):
        query = re.sub(r"(summarize|summary|explain)", "", query, flags=re.IGNORECASE).strip()

    print("🔍 Refined Query:", query)

    # =========================
    # 🤖 LLM TOOL SELECTION
    # =========================
    tool = decide_tool(original_query)
    print("🤖 LLM SELECTED TOOL:", tool)

    # =========================
    # 🔥 NEW: UPLOADED DOCUMENT PRIORITY
    # =========================
    
    print("🧠 Uploaded store keys:", uploaded_text_store.keys())
    print("🧠 Current user:", user_id)


    # ⚠️ IMPORTANT: make sure this exists at top of file
    # uploaded_text_store = {}

    if tool == "summarize" and user_id in uploaded_text_store:
        print("📄 Using uploaded document for summary")

        text = uploaded_text_store[user_id]

        if not text:
            return {
                "answer": "⚠️ Uploaded document is empty.",
                "tool": "Document Summary"
            }

        # limit size
        text = text[:20000]

        summary = summarize_text(text)

        return {
            "tool": "Document Summary",
            "answer": summary
        }

    # =========================
    # 🔍 STEP 1: SEARCH INDIAN KANOON
    # =========================
    try:
        import urllib.parse

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://indiankanoon.org/search/?formInput={encoded_query}"

        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=10, verify=False)
        cases = parse_indiankanoon(response.text)

        print(f"Fetched {len(cases)} cases")

    except Exception as e:
        print("❌ Fetch error:", e)
        cases = []

    # =========================
    # 🔵 TOOL: FETCH
    # =========================
    if tool == "fetch":

        exact = []
        related = []

        query_lower = query.lower()

        for c in cases:
            title = c["title"].lower()

            if query_lower in title:
                exact.append(c)
            else:
                related.append(c)

        final_cases = (exact + related)[:10]

        return {
            "tool": "fetch",
            "answer": "\n\n".join([
                f"Case: {c['title']}\nCitation: {c['citation']}\nLink: {c['link']}"
                for c in final_cases
            ])
        }

    # =========================
    # 🔥 STEP 2: SELECT CASES
    # =========================
    if tool == "summarize":
        selected = select_best_case(query, cases)

        if selected and len(selected) > 0:
            cases = selected
        else:
            print("⚠️ No strong match → fallback to first case")

        cases = cases[:1]

        print("✅ FINAL CASE SELECTED:", [c["title"] for c in cases])

    elif tool == "compare":

        import urllib.parse
        user_id = request.user_id or "guest"
        

        # =========================
        # 🔥 CLEAN QUERY
        # =========================
        query_clean = re.sub(r"\b(compare|with)\b", "", query, flags=re.IGNORECASE).strip()

        # normalize → always use AND
        query_clean = re.sub(r'\b(vs|versus|v\.)\b', 'and', query_clean, flags=re.IGNORECASE)

        parts = re.split(r'\band\b', query_clean, flags=re.IGNORECASE)
        parts = [p.strip() for p in parts if p.strip()]

        # =========================
        # 🔥 CASE: UPLOADED DOC EXISTS
        # =========================
        if has_uploaded_doc and "compare with" in original_query.lower():

            if len(parts) < 1:
                return {
                    "answer": "⚠️ Please provide a case to compare with uploaded document.",
                    "tool": "compare"
                }

            case_query = original_query.lower().replace("compare with", "").strip()

            print("📄 Using uploaded document")
            print("⚖️ Comparing with:", case_query)

            # 🔍 FETCH CASE FROM INDIAN KANOON
            encoded_q = urllib.parse.quote_plus(case_query)
            url = f"https://indiankanoon.org/search/?formInput={encoded_q}"

            try:
                res = requests.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=10,
                    verify=False
                )

                results = parse_indiankanoon(res.text)
                best = select_best_case(case_query, results)

                if not best:
                    return {
                        "answer": "⚠️ Could not find the case for comparison.",
                        "tool": "compare"
                    }

                external_case = best[0]
                print("✅ Selected:", external_case["title"])

            except Exception as e:
                print("❌ Error fetching case:", e)
                return {
                    "answer": "⚠️ Failed to fetch case.",
                    "tool": "compare"
                }

            # =========================
            # 🔥 BUILD CONTEXT
            # =========================
            context = ""

            # CASE 1 → uploaded doc
            context += f"Case 1: Uploaded Document\n{uploaded_text_store[user_id]}\n\n"

            # CASE 2 → fetched case
            print("📥 Fetching:", external_case["title"])
            text = fetch_case_context(external_case["link"])

            if not text:
                return {
                    "answer": "⚠️ Could not fetch case content.",
                    "tool": "compare"
                }

            context += f"""
            Case 2: {external_case['title']}

            Full Judgment:
            {text}
            """

            cases = [
                {"title": "Uploaded Document"},
                {"title": external_case["title"]}
            ]

        # =========================
        # 🔥 NORMAL CASE VS CASE
        # =========================
        else:

            if len(parts) < 2 and not has_uploaded_doc:
                return {
                    "answer": "⚠️ Please provide two cases using 'and'.",
                    "tool": "compare"
                }

            case1_query = parts[0]
            case2_query = parts[1]

            print("CASE 1:", case1_query)
            print("CASE 2:", case2_query)

            cases_data = []

            for q in [case1_query, case2_query]:

                encoded_q = urllib.parse.quote_plus(q)
                url = f"https://indiankanoon.org/search/?formInput={encoded_q}"

                print("🔍 Searching:", q)

                try:
                    res = requests.get(
                        url,
                        headers={"User-Agent": "Mozilla/5.0"},
                        timeout=10,
                        verify=False
                    )

                    results = parse_indiankanoon(res.text)
                    best = select_best_case(q, results)

                    if best and len(best) > 0:
                        cases_data.append(best[0])
                        print("✅ Selected:", best[0]["title"])
                    else:
                        print("⚠️ No match for:", q)

                except Exception as e:
                    print("❌ Error fetching case:", e)

            if len(cases_data) < 2:
                return {
                    "answer": "⚠️ Could not find both cases for comparison.",
                    "tool": "compare"
                }

            print("🎯 FINAL CASES:", [c["title"] for c in cases_data])

            # =========================
            # 🔥 FETCH CONTEXT
            # =========================
            context = ""

            for c in cases_data:
                print("📥 Fetching:", c["title"])

                text = fetch_case_context(c["link"])

                if text:
                    context += f"Case: {c['title']}\n{text}\n\n"

            cases = cases_data

    # =========================
    # 🔥 STEP 3: FETCH CONTEXT (ONLY IF NOT ALREADY BUILT)
    # =========================
    

    if not context:   # ✅ VERY IMPORTANT CHECK

        context = ""

        try:
            for case in cases:
                print("📥 Fetching:", case["title"])

                text = fetch_case_context(case["link"])

                print("TEXT LENGTH:", len(text) if text else 0)

                if text:
                    context += f"Case: {case['title']}\n{text}\n\n"

        except Exception as e:
            print("❌ Context fetch error:", e)

    # =========================
    # 🚨 FINAL CHECK
    # =========================
    if not context or context.strip() == "":
        return {
            "answer": "⚠️ Could not fetch case content.",
            "tool": tool
        }

    # 🔥 LIMIT SIZE
    if len(context) > 12000:
        context = context[:12000]

    print("TOTAL CONTEXT LENGTH:", len(context))

    # =========================
    # 🧠 PROMPT
    # =========================
    if tool == "summarize":
        prompt = f"""
You are a legal expert.

Extract structured information from the case.

Context:
{context}

STRICT FORMAT:

Facts:
- bullet points

Issue:
- bullet points

Judgment:
- bullet points

Reasoning:
- bullet points
"""
    else:
        prompt = f"""
You are a senior legal expert.

Compare the two cases deeply and precisely.

Context:
{context}

STRICT FORMAT:

Case 1: {cases[0]['title']}
Case 2: {cases[1]['title']}

Facts:
- Case 1:
- Case 2:

Issues:
- Case 1:
- Case 2:

Similarities:
- Legal principles
- Constitutional aspects

Differences:
- Scope
- Legal impact
- Articles involved

Judgment:
- Case 1:
- Case 2:

Final Insight:
- 2–3 lines explaining the core legal difference
"""

    # =========================
    # ⚡ MCP TOOL EXECUTION
    # =========================
    print("🚀 USING MCP TOOL...")
    # =========================
    # ✅ FINAL RETURN (CRITICAL)
    # =========================

    try:
        if tool == "summarize":
            result = tools["summarize"](context)

        elif tool == "compare":
            result = tools["compare"](context, cases)

        else:
            # fallback (rare)
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
            result = clean_llm_output(completion.choices[0].message.content)
        print("🧾 RESULT:", result[:500])  # ✅ ADD THIS


    except Exception as e:
        print("❌ LLM error:", e)
    # =========================
    # ✅ FINAL RETURN (CORRECT PLACE)
    # =========================

    if not result or str(result).strip() == "":
        result = "⚠️ No response generated. Try again."

    return {
        "answer": result,
        "tool": tool,
        "cases_used": [
            {
                "title": c.get("title"),
                "link": c.get("link")
            } for c in cases
        ] if isinstance(cases, list) else []
    }
# =========================
# 📄 SUMMARIZE CASE
# =========================
@app.post("/summarize-case")
def summarize_case(request: LinkRequest):

    text = fetch_full_judgment(request.link)

    if not text:
        return {"error": "Could not fetch judgment"}

    summary = summarize_text(text)

    return {"summary": summary}

# =========================
# 📂 FILE UPLOAD
# =========================
# 🔥 GLOBAL STORE (top of file)
# 🔥 GLOBAL STORE (KEEP THIS AT TOP OF FILE ONLY ONCE)
# =========================
# 📂 FILE UPLOAD (FIXED)
# =========================

from fastapi import UploadFile, File, Request

# 🔥 GLOBAL STORE (temporary - RAM)
uploaded_text_store = {}

@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):

    try:
        # =========================
        # 📂 READ FILE
        # =========================
        content = await file.read()
        text = extract_text(file.filename, content)

        # =========================
        # ❌ VALIDATIONS
        # =========================
        if text == "Unsupported file format":
            return {"error": "Unsupported file type"}

        if not text or not text.strip():
            return {"error": "Empty or unreadable document"}

        # =========================
        # 🔥 LIMIT SIZE
        # =========================
        text = text[:20000]

        # =========================
        # 🔐 GET USER ID (FIXED)
        # =========================
        user_id = request.headers.get("user-id")

        # fallback safety
        if not user_id:
            user_id = "guest"

        # =========================
        # 🔥 STORE PER USER
        # =========================
        uploaded_text_store[user_id] = text

        print("📄 Document stored for user:", user_id)
        print("📊 Stored users:", list(uploaded_text_store.keys()))
        print("TEXT LENGTH:", len(text))

        # =========================
        # ✅ RESPONSE
        # =========================
        return {
            "filename": file.filename,
            "message": "✅ Document uploaded successfully. Now ask: 'compare with <case name>'"
        }

    except Exception as e:
        print("❌ Upload error:", e)
        return {
            "error": "⚠️ Upload failed"
        }
        
@app.post("/fetch_cases")
async def fetch_cases_api(request: dict):

    import urllib.parse

    query = request.get("query", "")

    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://indiankanoon.org/search/?formInput={encoded_query}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=10, verify=False)

    cases = parse_indiankanoon(response.text)

    # =========================
    # 🔥 STRONG FILTERING
    # =========================
    query_words = query.lower().split()

    filtered = []
    for c in cases:
        title = c["title"].lower()

        match_score = sum(1 for w in query_words if w in title)

        if match_score >= 2:
            filtered.append(c)

    # fallback
    cases = filtered if filtered else cases[:5]

    return {
        "cases": cases
    }

# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
      # 🔥 run once

    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)