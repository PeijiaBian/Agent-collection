import config
from langchain_openai import ChatOpenAI
from crewai import Agent
import os

# 初始化 GPT-4o 模型
llm = ChatOpenAI(
    temperature=0.3,
    model_name="gpt-4o",  # 切换到 GPT-4o
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    openai_api_base=os.environ.get("OPENAI_API_BASE")
)

collector = Agent(
    role="信息采集员",
    goal="从输入的 company_name 和 search_result 中提取官网、职位、新闻和社交媒体链接",
    backstory=(
        "你会收到两个输入字段：\n"
        "  1. company_name（字符串，例如 “tiktok”）\n"
        "  2. search_result（字典，由 get_company_profile_from_search 返回，包含“official_website”、“job_links”、“news_links”、“social_media”）\n"
        "请严格使用这两个输入中的真实数据，返回如下格式的 JSON：\n"
        "{\n"
        "  \"official_website\": <URL 或 “未找到”>,\n"
        "  \"job_links\": [<URL 列表> 或 [“未找到”>],\n"
        "  \"news_links\": [<URL 列表> 或 [“未找到”>],\n"
        "  \"social_media\": {\n"
        "    \"linkedin\": <URL 或 “未找到”>,\n"
        "    \"facebook\": <URL 或 “未找到”>,\n"
        "    \"twitter\": <URL 或 “未找到”>\n"
        "  }\n"
        "}\n"
        "注意：不得编造任何信息，如果某项找不到就填“未找到”。"
    ),
    llm=llm
)

profiler = Agent(
    role="客户画像分析员",
    goal="基于信息采集结果生成客户画像",
    backstory=(
        "你会收到以下输入：\n"
        "  1. company_name\n"
        "  2. info_collector 输出的 JSON：\n"
        "     {\n"
        "       \"official_website\": ..., \n"
        "       \"job_links\": [...],\n"
        "       \"news_links\": [...],\n"
        "       \"social_media\": { ... }\n"
        "     }\n"
        "请基于这些信息，生成如下格式的 JSON：\n"
        "{\n"
        "  \"industry\": <行业，如无法判断填“未知”>,\n"
        "  \"location\": <地点，如无法判断填“未知”>,\n"
        "  \"is_hiring\": <true/false，如果 job_links 中至少有一项不为 “未找到” 则为 true，否则 false>,\n"
        "  \"is_funded\": <true/false，如果 news_links 中包含“融资”或“funding”相关，则为 true，否则 false>\n"
        "}\n"
        "如果无法从输入中确定，则 industry/location 填“未知”，is_hiring/is_funded 填 false。"
    ),
    llm=llm
)

matcher = Agent(
    role="潜在客户识别员",
    goal="根据 ICP 规则判断客户是否高潜",
    backstory=(
        "你会收到以下输入：\n"
        "  1. company_name\n"
        "  2. info_collector 输出的 JSON：{\"official_website\":..., \"job_links\":..., \"news_links\":..., \"social_media\":{...}}\n"
        "  3. profiler 输出的 JSON：{\"industry\":..., \"location\":..., \"is_hiring\":..., \"is_funded\":...}\n"
        "请根据以下 ICP 规则判断并返回 JSON：\n"
        "  a) industry 中必须包含“Tech”或“technology”；\n"
        "  b) job_links 列表中至少有一个包含 “Engineer” 或 “Developer”；\n"
        "  c) news_links 中至少有一条包含 “融资” 或 “funding” 关键词。\n"
        "如果以上三项都满足，则返回：\n"
        "{ \"high_potential\": true, \"reason\": \"<说明满足哪些条件>\" }\n"
        "否则返回：\n"
        "{ \"high_potential\": false, \"reason\": \"<说明未满足哪些条件>\" }\n"
        "请严格使用输入字段，不得编造额外信息。"
    ),
    llm=llm
)

intent_analyst = Agent(
    role="购买意图分析员",
    goal="从岗位与新闻链接中识别采购意图信号",
    backstory=(
        "你会收到以下输入：\n"
        "  1. company_name\n"
        "  2. info_collector 输出的 JSON\n"
        "  3. profiler 输出的 JSON\n"
        "  4. matcher 输出的 JSON\n"
        "请检查 job_links 是否包含 “AI Engineer”、“CRM Manager”、“DevOps Engineer” 等关键词；\n"
        "检查 news_links 是否包含 “购买”、“部署”、“系统升级”、“采购” 等关键词。\n"
        "如果检测到任意一个信号，则返回：\n"
        "{ \"purchase_intent\": \"Yes\", \"signals\": [<列出信号>], \"reason\": \"<说明>\" }\n"
        "否则返回：\n"
        "{ \"purchase_intent\": \"No\", \"signals\": [], \"reason\": \"<说明未检测到信号>\" }\n"
        "请仅使用输入字段中的信息，不要编造数据。"
    ),
    llm=llm
)

reporter = Agent(
    role="销售线索汇报员",
    goal="整合所有中间结果并输出最终 JSON 报告",
    backstory=(
        "你会收到以下输入：\n"
        "  1. company_name（原始公司名）\n"
        "  2. info_collector 输出的 JSON\n"
        "  3. profiler 输出的 JSON\n"
        "  4. matcher 输出的 JSON\n"
        "  5. intent_analyst 输出的 JSON\n"
        "请基于这些输入，按以下格式输出一个完整的 JSON 报告：\n"
        "{\n"
        "  \"company_name\": \"<原始 company_name>\",\n"
        "  \"customer_information\": { <来自 info_collector> },\n"
        "  \"customer_profile\": { <来自 profiler> },\n"
        "  \"potential_evaluation\": { <来自 matcher> },\n"
        "  \"purchase_intent\": { <来自 intent_analyst> }\n"
        "}\n"
        "其中“company_name”字段必须填写你收到的原始公司名，其余字段严格对应前序输出。"
    ),
    llm=llm
)
