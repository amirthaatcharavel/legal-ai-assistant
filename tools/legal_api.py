import requests
from bs4 import BeautifulSoup
import urllib.parse

# 🔥 Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =========================
# 🔥 GLOBAL DRIVER (OPTIMIZED)
# =========================
driver = None

def get_driver():
    global driver
    if driver is None:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
    return driver


# =========================
# 🔥 CLEAN QUERY (ONLY ONCE)
# =========================
def clean_query(query):
    noise = ["case", "summarize", "explain", "judgment", "law"]
    q = query.lower()

    for n in noise:
        q = q.replace(n, "")

    return q.strip()


# =========================
# 🔥 GARBAGE FILTER
# =========================
def is_garbage_query(query):
    return len(query.strip()) < 3


# =========================
# 🔥 STRONG RELEVANCE SCORE
# =========================
def calculate_relevance_score(title, query):
    title = title.lower()
    query = query.lower()

    score = 0

    if query.strip() == title.strip():
        score += 500

    if query in title:
        score += 200

    words = query.split()
    match_count = sum(1 for w in words if w in title)
    score += match_count * 25

    important_cases = [
        "kesavananda bharati",
        "maneka gandhi",
        "minerva mills",
        "puttaswamy",
        "a.k. gopalan"
    ]

    for case in important_cases:
        if case in title:
            score += 100

    return score


# =========================
# 🔥 SMART QUERY MAP (STRONG)
# =========================
def smart_query_map(query):
    q = query.lower()

    if any(word in q for word in ["kesavananda", "bharati", "basic structure"]):
        return "Kesavananda Bharati vs State of Kerala 1973"

    if "privacy" in q:
        return "Justice K.S. Puttaswamy vs Union of India"

    if "personal liberty" in q:
        return "Maneka Gandhi vs Union of India"

    return query


import re

def is_best_match(title, query):
    title = title.lower()
    query = query.lower()

    # Extract meaningful words
    title_words = set(re.findall(r'\w+', title))
    query_words = set(re.findall(r'\w+', query))

    # Remove weak/common words
    stopwords = {"vs", "v", "and", "or", "of", "the", "in", "on", "an"}
    title_words = title_words - stopwords
    query_words = query_words - stopwords

    # Count overlap
    match_count = len(title_words & query_words)

    # Strong match threshold
    if match_count >= max(2, len(query_words) // 2):
        return True
    # Landmark case boost (backup)
    important_cases = [
        "kesavananda bharati",
        "maneka gandhi",
        "minerva mills",
        "puttaswamy",
        "a.k. gopalan"
    ]

    for case in important_cases:
        if case in title and case in query:
            return True

    return False
# =========================
# 🔥 REQUESTS SCRAPER (FIXED)
# =========================
def fetch_requests(query, original_query, year=None, court=None):

    encoded = urllib.parse.quote(query)
    url = f"https://indiankanoon.org/search/?formInput={encoded}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        print("🔍 Requests URL:", url)

        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        items = soup.select(".result")

        if not items:
            print("⚠️ Requests found no results")
            return []

        results = []  # ✅ MUST be before loop

        for item in items:
            a = item.find("a")
            if not a:
                continue

            title = a.get_text(strip=True)
            link = "https://indiankanoon.org" + a["href"]

            results.append({
                "title": title,
                "link": link,
                "source": "Indian Kanoon",
                "score": calculate_relevance_score(title, original_query),
                "best_match": is_best_match(title, original_query)
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]

    except Exception as e:
        print("❌ Requests error:", e)
        return []
# =========================
# 🔥 SELENIUM SCRAPER (FIXED)
# =========================
def fetch_selenium(query, original_query, year=None, court=None):

    driver = get_driver()

    try:
        encoded = urllib.parse.quote(query)
        url = f"https://indiankanoon.org/search/?formInput={encoded}"

        print("🌐 Selenium URL:", url)

        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "result"))
        )

        items = driver.find_elements(By.CLASS_NAME, "result")

        results = []

        for item in items:
            try:
                a = item.find_element(By.TAG_NAME, "a")

                title = a.text
                link = a.get_attribute("href")
                results.append({
    "title": title,
    "link": link,
    "source": "Indian Kanoon",
    "score": calculate_relevance_score(title, original_query),
    "best_match": is_best_match(title, original_query)
})

            except:
                continue

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]

    except Exception as e:
        print("❌ Selenium error:", e)
        return []


# =========================
# 🔥 MAIN FETCH (STRONG FALLBACK)
# =========================
def fetch_from_indian_kanoon(query, original_query, year=None, court=None):

    results = fetch_requests(query, original_query, year, court)

    if results and len(results) >= 3:
        return results

    print("⚡ Switching to Selenium...")

    selenium_results = fetch_selenium(query, original_query, year, court)

    return selenium_results if selenium_results else results


# =========================
# 🔥 WIKIPEDIA FALLBACK
# =========================
def fetch_wikipedia_cases(query):

    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}+case&format=json"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        results = []

        for item in data.get("query", {}).get("search", [])[:5]:
            title = item["title"]

            results.append({
                "title": title,
                "link": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                "source": "Wikipedia",
                "score": 50
            })

        return results

    except:
        return []


# =========================
# 🔥 REMOVE DUPLICATES (STRONG)
# =========================
def deduplicate(results):
    seen = set()
    unique = []

    for r in results:
        key = re.sub(r'\W+', '', r["title"].lower())

        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique


# =========================
# 🔥 FINAL OUTPUT
# =========================
def fetch_case_context(link):
    import requests
    from bs4 import BeautifulSoup
    import re

    headers = {"User-Agent": "Mozilla/5.0"}

    print("LINK:", link)

    # =========================
    # 🔥 EXTRACT DOC ID
    # =========================
    match = re.search(r'/doc(?:fragment)?/(\d+)/', link)

    if not match:
        print("❌ No doc ID found")
        return None

    doc_id = match.group(1)
    print("DOC ID:", doc_id)

    MAX_CHARS = 15000  # 🔥 IMPORTANT LIMIT

    # =========================
    # 🔥 STEP 1: TRY FRAGMENT
    # =========================
    try:
        frag_url = f"https://indiankanoon.org/docfragment/{doc_id}/?big=0"
        print("🌐 Fragment URL:", frag_url)

        res = requests.get(frag_url, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        text = soup.get_text(" ", strip=True)

        print("FRAGMENT LENGTH:", len(text))

        if (
            text
            and len(text) > 500
            and "Indian Kanoon" not in text[:200]
            and "Search" not in text[:200]
        ):
            text = clean_text(text)

            # 🔥 TRIM LARGE TEXT
            if len(text) > MAX_CHARS:
                print("⚡ Trimming large fragment...")
                text = text[:MAX_CHARS]

            return text

    except Exception as e:
        print("❌ Fragment error:", e)

    # =========================
    # 🔥 STEP 2: FULL DOCUMENT
    # =========================
    try:
        full_url = f"https://indiankanoon.org/doc/{doc_id}/"
        print("🌐 FULL DOC URL:", full_url)

        # 🔥 Increased timeout
        res = requests.get(full_url, headers=headers, verify=False, timeout=25)
        soup = BeautifulSoup(res.text, "html.parser")

        # ✅ PRIMARY CONTENT
        judgment = soup.find("div", {"class": "judgments"})

        if judgment:
            text = judgment.get_text(" ", strip=True)
            print("FULL DOC LENGTH:", len(text))

            if text and len(text) > 500:
                text = clean_text(text)

                # 🔥 TRIM LARGE TEXT
                if len(text) > MAX_CHARS:
                    print("⚡ Trimming large full doc...")
                    text = text[:MAX_CHARS]

                return text

        # =========================
        # 🔥 FALLBACK (SAFE)
        # =========================
        text = soup.get_text(" ", strip=True)
        print("FULL PAGE RAW LENGTH:", len(text))

        if text and len(text) > 500:
            text = clean_text(text)

            if len(text) > MAX_CHARS:
                print("⚡ Trimming fallback text...")
                text = text[:MAX_CHARS]

            return text

    except Exception as e:
        print("❌ Full doc error:", e)

    return None


# =========================
# 🔥 CLEAN TEXT (IMPORTANT)
# =========================
def clean_text(text):
    import re

    # remove navigation / UI junk
    text = re.sub(r"Skip to main content.*?Search", "", text, flags=re.DOTALL)
    text = re.sub(r"Indian Kanoon.*?Login", "", text, flags=re.DOTALL)

    # remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()

import atexit

def close_driver():
    global driver
    if driver:
        driver.quit()

atexit.register(close_driver)

import re

def extract_case_data(title_text, snippet_text):
    # YEAR
    year_match = re.search(r'\b(19|20)\d{2}\b', title_text)
    year = year_match.group() if year_match else None

    # COURT
    court = None
    if "supreme court" in snippet_text.lower():
        court = "Supreme Court"
    elif "high court" in snippet_text.lower():
        court = "High Court"

    # CITATION
    citation_match = re.search(r'\(\d{4}.*?\)', snippet_text)
    citation = citation_match.group() if citation_match else None

    return court, year, citation


    # =========================
# 🔥 FINAL FETCH CASES (MISSING FUNCTION)
# =========================
def fetch_cases(query, year=None, court=None):

    if is_garbage_query(query):
        return []

    print("🧠 Original Query:", query)

    query_mapped = smart_query_map(query)
    print("🧠 Mapped Query:", query_mapped)

    clean_q = clean_query(query_mapped)
    print("🧠 Clean Query:", clean_q)

    # 🔥 main fetch
    results = fetch_from_indian_kanoon(clean_q, query_mapped, year, court)

    # 🔥 fallback retry
    if not results:
        print("⚡ Retrying original query...")
        results = fetch_from_indian_kanoon(query, query, year, court)

    # 🔥 wikipedia fallback
    if len(results) < 3:
        results += fetch_wikipedia_cases(query)

    # 🔥 remove duplicates
    results = deduplicate(results)

    # 🔥 best match first
    results.sort(key=lambda x: (not x.get("best_match", False), -x.get("score", 0)))

    return results[:5]