import time
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException

def safe_ddg_search(query, max_results=5, retries=3, delay=5):
    for attempt in range(retries):
        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=max_results)
                return list(results)
        except DuckDuckGoSearchException as e:
            print(f"[警告] 请求被限速，第 {attempt + 1} 次重试中...：{e}")
            time.sleep(delay)
    return []

def search_company_website(company_name):
    results = safe_ddg_search(f"{company_name} official website")
    for res in results:
        if "www." in res.get("href", ""):
            return res["href"]
    return "未找到官网"

def search_company_news(company_name):
    results = safe_ddg_search(f"{company_name} news")
    return [res["href"] for res in results if "http" in res.get("href", "")] or ["未找到相关新闻"]

def search_social_links(company_name):
    linkedin = "未找到"
    facebook = "未找到"

    results = safe_ddg_search(f"{company_name} LinkedIn site:linkedin.com", max_results=2)
    linkedin = next((res["href"] for res in results if "linkedin.com/company" in res["href"]), "未找到")

    results = safe_ddg_search(f"{company_name} Facebook site:facebook.com", max_results=2)
    facebook = next((res["href"] for res in results if "facebook.com" in res["href"]), "未找到")

    return {
        "LinkedIn": linkedin,
        "Facebook": facebook
    }

def get_company_profile_from_search(company_name):
    return {
        "公司官网": search_company_website(company_name),
        "新闻": search_company_news(company_name),
        "社交媒体": search_social_links(company_name)
    }
