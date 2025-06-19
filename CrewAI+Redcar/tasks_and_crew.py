from crewai import Task, Crew
from agents import collector, profiler, matcher, intent_analyst, reporter

# Task 1: Data Collection
task_collect = Task(
    description="""
    【Task1: 信息采集】

    你会收到两个输入字段：
      1. company_name: {company_name}
      2. search_result: {search_result}

    请严格基于这两项输入，返回如下 JSON：
    {
      "official_website": "<URL 或 \"Not Found\">",
      "job_links": ["<URL>", ...] 或 ["Not Found"],
      "news_links": ["<URL>", ...] 或 ["Not Found"],
      "social_media": {
        "linkedin": "<URL 或 \"Not Found\">",
        "facebook": "<URL 或 \"Not Found\">",
        "twitter": "<URL 或 \"Not Found\">"
      }
    }

    注意：仅使用 search_result 中的真实链接；如果某项未找到则填 “Not Found”。
    """,
    expected_output="Data Collector 输出的 JSON",
    agent=collector
)

# Task 2: Customer Profile Analysis
task_profile = Task(
    description="""
    【Task2: 客户画像分析】

    你会收到：
      1. company_name: {company_name}
      2. Data Collector 输出的 JSON:
         {
           "official_website": ...,
           "job_links": [...],
           "news_links": [...],
           "social_media": { ... }
         }

    请基于这些输入，生成如下格式的 JSON：
    {
      "industry": "<string 或 \"Unknown\">",
      "location": "<string 或 \"Unknown\">",
      "is_hiring": <true 或 false>,
      "is_funded": <true 或 false>
    }

    - 如果 job_links 中至少有一项不为 "Not Found" 则 is_hiring 为 true，否则为 false。
    - 如果 news_links 中包含 "融资" 或 "funding" 则 is_funded 为 true，否则为 false。
    - 无法判断字段时，industry/location 填 "Unknown"，is_hiring/is_funded 填 false。
    """,
    expected_output="Profile Analyst 输出的 JSON",
    agent=profiler
)

# Task 3: ICP Matcher
task_match = Task(
    description="""
    【Task3: ICP 潜在客户识别】

    你会收到：
      1. company_name: {company_name}
      2. Data Collector 输出的 JSON:
         {
           "official_website": ...,
           "job_links": [...],
           "news_links": [...],
           "social_media": { ... }
         }
      3. Profile Analyst 输出的 JSON:
         {
           "industry": ...,
           "location": ...,
           "is_hiring": ...,
           "is_funded": ...
         }

    请根据以下 ICP 规则判断是否为高潜客户，并返回 JSON：
      a. industry 中必须包含 “Tech” 或 “technology”；
      b. job_links 列表中至少有一个链接包含 “Engineer” 或 “Developer”；
      c. news_links 列表中至少有一条包含 “融资” 或 “funding” 字段。

    如果以上三条内容都满足，则输出：
    {
      "high_potential": true,
      "reason": "<简要说明满足哪些条件>"
    }
    否则输出：
    {
      "high_potential": false,
      "reason": "<说明未满足哪些条件>"
    }

    只使用输入数据，不能编造信息。
    """,
    expected_output="ICP Matcher 输出的 JSON",
    agent=matcher
)

# Task 4: Purchase Intent Analysis
task_intent = Task(
    description="""
    【Task4: 购买意图分析】

    你会收到：
      1. company_name: {company_name}
      2. Data Collector 输出的 JSON:
         {
           "official_website": ...,
           "job_links": [...],
           "news_links": [...],
           "social_media": { ... }
         }
      3. Profile Analyst 输出的 JSON:
         {
           "industry": ...,
           "location": ...,
           "is_hiring": ...,
           "is_funded": ...
         }
      4. ICP Matcher 输出的 JSON:
         {
           "high_potential": <true/false>,
           "reason": "<...>"
         }

    检查 job_links 中是否有 “AI Engineer”、“CRM Manager”、“DevOps Engineer” 等关键词，\n
    检查 news_links 中是否有 “购买”、“部署”、“系统升级”、“采购” 等关键词。\n
    如果检测到任意一个信号，则返回：
    {
      "purchase_intent": "Yes",
      "signals": [<列出相关岗位或关键词>],
      "reason": "<简要说明依据>"
    }
    否则返回：
    {
      "purchase_intent": "No",
      "signals": [],
      "reason": "<说明未检测到采购信号>"
    }

    请严格使用输入字段，不能添加虚假信息。
    """,
    expected_output="Intent Analyst 输出的 JSON",
    agent=intent_analyst
)

# Task 5: Final Report Merge
task_report = Task(
    description="""
    【Task5: 最终报告合并】

    你会收到：
      1. company_name: {company_name}
      2. Data Collector 输出的 JSON:
         {
           "official_website": ...,
           "job_links": [...],
           "news_links": [...],
           "social_media": { ... }
         }
      3. Profile Analyst 输出的 JSON:
         {
           "industry": ...,
           "location": ...,
           "is_hiring": ...,
           "is_funded": ...
         }
      4. ICP Matcher 输出的 JSON:
         {
           "high_potential": <true/false>,
           "reason": "<...>"
         }
      5. Intent Analyst 输出的 JSON:
         {
           "purchase_intent": "<Yes/No>",
           "signals": [...],
           "reason": "<...>"
         }

    基于以上输入，输出一个完整的 JSON 报告，格式如下（**注意键名必须与示例一致**）：
    {
      "company_name": "{company_name}",
      "customer_information": {
        "official_website": <来自 Task1>,
        "job_links": <来自 Task1>,
        "news_links": <来自 Task1>,
        "social_media": {
          "linkedin": <来自 Task1>,
          "facebook": <来自 Task1>,
          "twitter": <来自 Task1>
        }
      },
      "customer_profile": {
        "industry": <来自 Task2>,
        "location": <来自 Task2>,
        "is_hiring": <来自 Task2>,
        "is_funded": <来自 Task2>
      },
      "potential_evaluation": {
        "high_potential": <来自 Task3>,
        "reason": "<来自 Task3>"
      },
      "purchase_intent": {
        "purchase_intent": "<来自 Task4>",
        "signals": <来自 Task4>,
        "reason": "<来自 Task4>"
      }
    }

    其中：
    - “company_name”字段一定要填你收到的原始字符串 {company_name}。
    - 其余字段必须严格对应前序 Agents 的输出 JSON。
    """,
    expected_output="Report Generator 输出的 JSON",
    agent=reporter
)

crew = Crew(
    agents=[collector, profiler, matcher, intent_analyst, reporter],
    tasks=[task_collect, task_profile, task_match, task_intent, task_report],
    verbose=True
)
