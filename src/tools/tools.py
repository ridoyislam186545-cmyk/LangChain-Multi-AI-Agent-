from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re
load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information of a topic . Returns title
    """
    results= tavily.search(query=query,max_results=5)
    out = []
    for r in results['results']:
        out.append(
            f"Title:{r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
          )
    return "\n----\n".join(out)
   
   
   
   
@tool
def scrape_url(url: str) -> str:
    """
    একটি URL থেকে মূল টেক্সট বের করে আনার ফাংশন।
    """
    # ১. হেডার সেট করা (অনেক ওয়েবসাইট বট ব্লক করে, তাই ইউজার-এজেন্ট দরকার)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # ২. পেজ ডাউনলোড করা
        print(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # HTTP Error থাকলে সেটা ধরবে
        html = response.text

        # ৩. Strategy 1: trafilatura দিয়ে চেষ্টা করা (সবচেয়ে ভালো কাজ করে)
        text = trafilatura.extract(html)
        if text and len(text.strip()) > 100:
            return text.strip()

        # ৪. Strategy 2: readability-lxml দিয়ে চেষ্টা করা
        doc = Document(html)
        clean_html = doc.summary()
        soup_readability = BeautifulSoup(clean_html, "html.parser")
        text = soup_readability.get_text(separator=" ", strip=True)
        if text and len(text.strip()) > 100:
            return text.strip()

        # ৫. Strategy 3: ফলব্যাক (Fallback) - আপনার ছবির কোড
        # যদি উপরের দুটি কাজ না করে, তবে পুরো পেজ থেকে অপ্রয়োজনীয় ট্যাগ মুছে ফেলা
        soup = BeautifulSoup(html, "html.parser")

        # অপ্রয়োজনীয় ট্যাগগুলো ডিলিট করা
        for tag in soup([
            "script", "style", "nav", "footer", 
            "header", "aside", "form", "iframe", "noscript"
        ]):
            tag.decompose()

        # শুধু টেক্সট বের করা
        text = soup.get_text(separator=" ", strip=True)
        
        # অতিরিক্ত স্পেস পরিষ্কার করা
        import re
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}"
    except Exception as e:
        return f"An error occurred: {e}"


# --- ব্যবহারের উদাহরণ ---
if __name__ == "__main__":
    target_url = "https://example.com" # এখানে আপনার টার্গেট ওয়েবসাইটের লিংক দিন
    result = scrape_url(target_url)
    print("\n--- Extracted Text ---")
    print(result[:500]) # প্রথম ৫০০ অক্ষর প্রিন্ট করবে