import os
import requests

SERP_API_KEY = os.getenv("SERPAPI_KEY")

def google_search(query, num_results=5):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY,
        "num": num_results
    }
    response = requests.get(url, params=params)
    results = response.json().get("organic_results", [])
    return [{"title": r.get("title"), "link": r.get("link")} for r in results]

def get_company_profile_from_search(company_name):
    return {
        "公司官网": google_search(f"{company_name} official site", 1)[0]["link"],
        "新闻": [r["link"] for r in google_search(f"{company_name} news")],
        "社交媒体": {
            "LinkedIn": google_search(f"{company_name} LinkedIn site:linkedin.com", 1)[0]["link"],
            "Facebook": google_search(f"{company_name} Facebook site:facebook.com", 1)[0]["link"]
        },
        "招聘岗位": [r["title"] for r in google_search(f"{company_name} hiring jobs site:greenhouse.io")]
    }
