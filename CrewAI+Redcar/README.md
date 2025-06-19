# AI Agent Orchestrator  
智能 Agent 编排系统

> 一个多工具、多模块集成的 Python 应用，用于管理、调度和运行各类 AI Agent 任务。  
> A Python application that integrates multiple tools and modules to orchestrate, schedule, and execute various AI Agent tasks.

---

## 一、简介 Introduction

**中文：**  
本项目通过 `agents.py`、`tasks_and_crew.py` 等模块，实现对不同 AI Agent 的统一管理与调用，支持 SerpAPI 搜索、Tavily 数据抓取、通用 Web 请求等能力。可用于快速搭建定制化智能工作流。

**English:**  
This project provides a unified framework—via modules like `agents.py` and `tasks_and_crew.py`—to register, schedule, and run diverse AI Agents. It supports SerpAPI searches, Tavily data extraction, generic web requests, and more, enabling rapid assembly of bespoke intelligent workflows.

---

## 二、主要功能 Features

| 功能                                | 描述 (中文)                                                                                                             | Description (English)                                                                                                   |
|-------------------------------------|-------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| **Agent 管理**                       | 在 `agents.py` 中集中注册和加载各类 Agent 类，并统一接口调用。                                                             | Centralized registration and loading of Agent classes in `agents.py`, exposed via a common interface.                  |
| **任务与队列**                       | `tasks_and_crew.py` 定义任务队列（Crew），支持并发调度和状态跟踪。                                                         | Defines task queues (“Crew”) in `tasks_and_crew.py`, supporting concurrent scheduling and state tracking.               |
| **外部搜索集成**                     | `serpapi_tools.py` 封装 SerpAPI 调用，用于网页检索和结构化结果返回。                                                       | Wraps SerpAPI calls in `serpapi_tools.py` for web searches and structured result returns.                                |
| **数据抓取工具**                     | `tavily_tool.py` 提供灵活的数据爬取接口，可配置爬取深度、过滤规则等。                                                       | Provides configurable data-scraping utilities in `tavily_tool.py`, supporting depth limits and filter rules.            |
| **通用 Web 工具**                    | `utils_web.py` 包括 HTTP 请求、超时重试、代理配置等常用网络功能模块。                                                     | Includes common networking utilities in `utils_web.py`: HTTP requests, retry logic, proxy support, etc.                 |
| **配置管理**                         | `config.py` 支持 YAML/环境变量混合加载，统一管理 API 密钥、调度参数、日志级别等。                                           | Supports YAML/env-var hybrid loading in `config.py`, centralizing API keys, scheduler settings, logging levels, etc.    |
| **CLI 与入口**                       | `main.py` 提供命令行接口，可按任务名称触发单个 Agent，也可启动 HTTP 服务或调度守护进程。                                   | `main.py` offers a CLI to trigger individual Agents by name, or launch an HTTP server or scheduler daemon.             |

---

## 三、项目结构 Project Structure

```

.
├── agents.py               # 统一注册与加载各类 Agent
├── tasks\_and\_crew\.py       # 任务队列（Crew）与调度逻辑
├── serpapi\_tools.py        # SerpAPI 搜索封装
├── tavily\_tool.py          # 数据抓取工具
├── utils\_web.py            # 通用 HTTP/网络工具
├── config.py               # 配置加载与管理
├── main.py                 # 命令行入口与服务启动
├── requirements.txt        # Python 依赖列表
└── README.md               # 本说明文档

````

---

## 四、安装 Installation

```bash
git clone https://github.com/your-org/ai-agent-orchestrator.git
cd ai-agent-orchestrator

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
````

---

## 五、使用 Usage

### 5.1 命令行触发单一 Agent / CLI: single Agent

```bash
python main.py run-agent --name "SearchAgent" --params '{"query":"OpenAI GPT-4"}'
```

* `--name`：Agent 类名
* `--params`：JSON 格式的输入参数

### 5.2 启动 HTTP 服务 / Start HTTP Server

```bash
python main.py serve --host 0.0.0.0 --port 8000
```

* 启动 FastAPI（或 Flask）兼容的 RESTful 接口，动态调用 Agent。

### 5.3 启动调度守护进程 / Daemon Scheduler

```bash
python main.py scheduler
```

* 根据 `config.py` 中的计划任务定义，自动执行定时 Agent。

---

## 六、配置 Configuration

```yaml
# config.yaml
serpapi:
  api_key: "YOUR_SERPAPI_KEY"
tavily:
  base_url: "https://api.tavily.io"
scheduler:
  interval_minutes: 15
logging:
  level: "INFO"
  file: "app.log"
```

* 也可通过环境变量覆盖：`export SERPAPI_API_KEY="..."`

---

## 七、依赖 Requirements

```text
pydantic
fastapi
uvicorn
requests
PyYAML
tavily-sdk
google-search-results  # SerpAPI client
schedule               # 任务调度
```

---

## 八、示例 Example

```bash
# 1. 运行一次 Web 搜索 Agent
python main.py run-agent --name "WebSearchAgent" --params '{"query":"最新AI技术"}'

# 2. 使用 Tavily 抓取新闻数据
python main.py run-agent --name "TavilyScrapeAgent" --params '{"url":"https://news.example.com","depth":2}'

# 3. 启动服务并通过 HTTP 调用
python main.py serve
curl -X POST http://localhost:8000/agents/WebSearchAgent \
     -H "Content-Type: application/json" \
     -d '{"query":"OpenAI"}'
```

---

## 九、未来计划 Future Work

* 增加更多 Agent 插件：社交媒体分析、舆情监测、表格数据处理
* 图形化控制台：可视化任务队列状态与历史
* 分布式调度：支持多节点协同执行

---
