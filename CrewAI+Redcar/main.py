from tasks_and_crew import crew
from tavily_tool import get_company_profile_from_search

# 要分析的公司列表
company_list = ["Microsoft"]

for company in company_list:
    print(f"\n🚀 正在分析公司：{company}\n")

    # 第 1 步：使用 Tavily 获取结构化搜索结果
    search_result = get_company_profile_from_search(company)

    # 第 2 步：将英文字段 company_name 和 search_result 传给 CrewAI
    result = crew.kickoff(inputs={
        "company_name": company,
        "search_result": search_result
    })

    # 输出最终 JSON 报告
    print("💼 最终结构化输出：")
    print(result)
    print("\n" + "=" * 80 + "\n")
