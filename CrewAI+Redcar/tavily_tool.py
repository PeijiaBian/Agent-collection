import os
import requests

# 从环境变量读取你的 Tavily API Key
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

def tavily_search(query: str, max_results: int = 25) -> list:
    """
    使用 Tavily API 的 POST /search 接口进行查询，并返回一个结果列表。
    每个结果为字典，至少包含 "title" 和 "url" 两个字段（如果有）。
    """
    url = "https://api.tavily.com/search"
    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,              # 要搜索的关键词
        "topic": "general",          # 使用通用主题
        "search_depth": "basic",     # 基础搜索深度
        "chunks_per_source": 3,      # 每个来源最多返回 3 个片段（非必需，可根据需要调整）
        "max_results": max_results,  # 最多返回几条结果
        "time_range": None,          # 不限制时间范围
        "days": 7,                   # 如果 time_range 为 None, 这一项暂时可以忽略
        "include_answer": False,     # 不需要 Tavily 的 “直接回答”
        "include_raw_content": False,
        "include_images": False,
        "include_image_descriptions": False,
        "include_domains": [],       # 如果想限制域名，可在这里列入，比如 ["tavily.com"]
        "exclude_domains": []        # 排除某些域名
    }

    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        # 打印错误信息，并返回空列表；上线时可改为记录日志
        print(f"Tavily API error: {resp.status_code} {resp.text}")
        return []

    data = resp.json()
    # 官方示例返回的 JSON 中，“results” 键下即为搜索结果列表
    # 格式示例：{"results": [{"title":"...","url":"...","snippet":"..."}, ...], ...}
    raw_results = data.get("results", [])
    # 只保留 title 和 url 两个字段
    parsed = []
    for item in raw_results:
        title = item.get("title", "").strip()
        url = item.get("url", "").strip()
        if title and url:
            parsed.append({"title": title, "url": url})
    return parsed


def get_company_profile_from_search(company_name: str) -> dict:
    """
    根据输入的公司名，调用 tavily_search，然后从返回结果中提取以下字段：
      • 公司官网
      • 招牌职位（careers/jobs）
      • 新闻链接（news/press/launch/raises/融资）
      • 社交媒体链接（LinkedIn/Facebook/Twitter）
    返回一个字典，结构为：
    {
      "公司官网": <string 或 "未找到">,
      "招牌职位": [<list of URLs> 或 ["未找到"]],
      "新闻": [<list of URLs> 或 ["未找到"]],
      "社交媒体": {
         "LinkedIn": <string 或 "未找到">,
         "Facebook": <string 或 "未找到">,
         "Twitter": <string 或 "未找到">
      }
    }
    """
    # 用公司名进行搜索，取最多 10 条结果
    results = tavily_search(company_name, max_results=10)

    def extract_link(keywords: list) -> str:
        """
        从 results 中找到第一个 title 或 url 中包含任何 keyword 的条目，返回其 URL。
        如果都没匹配到，则返回 "未找到"。
        """
        for r in results:
            combined = (r["title"] + " " + r["url"]).lower()
            for kw in keywords:
                if kw.lower() in combined:
                    return r["url"]
        return "未找到"

    def extract_all_links(keywords: list) -> list:
        """
        返回所有 title 或 url 中包含任何 keyword 的结果 URL 列表。
        如果没有匹配到，返回 ["未找到"]。
        """
        matched = []
        for r in results:
            combined = (r["title"] + " " + r["url"]).lower()
            for kw in keywords:
                if kw.lower() in combined:
                    matched.append(r["url"])
                    break
        return matched if matched else ["未找到"]

    return {
        "公司官网": extract_link([company_name.lower(), "官网", "official site", ".com"]),
        "招牌职位": extract_all_links(["careers", "join us", "jobs", "hiring"]),
        "新闻": extract_all_links(["news", "press", "launch", "raises", "融资"]),
        "社交媒体": {
            "LinkedIn": extract_link(["linkedin.com"]),
            "Facebook": extract_link(["facebook.com"]),
            "Twitter": extract_link(["twitter.com", "x.com"]),
        }
    }
