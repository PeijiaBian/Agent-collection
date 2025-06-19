# Email Group Sender Agent 

> 一个基于 Dify 平台和自研邮件工具的微服务，支持批量发送邮件（To／Cc／Bcc），并生成发送统计报告。  
> A microservice built on Dify and a custom email tool, supporting batch email delivery (To/Cc/Bcc) with aggregated send-report generation.

---


## 简介 Introduction

**中文：**  
Email Group Sender Agent 允许用户上传一个包含收件人邮箱列表的 Excel 文件（或直接输入收件人地址），指定主题和正文，通过 To、Cc、Bcc 三种方式批量发送邮件；支持自定义 SMTP 服务，并在发送完成后自动调用 LLM 生成 Markdown 格式的发送统计报告。

**English:**  
The Email Group Sender Agent lets users upload an Excel file containing recipient addresses (or input them directly), set subject and body, and send batch emails via To, Cc, and Bcc. It supports custom SMTP settings and, upon completion, invokes an LLM to produce a Markdown‐formatted send‐report.

---

## 主要功能 Key Features

| 功能                                         | 描述                                                                                               |
|---------------------------------------------|---------------------------------------------------------------------------------------------------|
| **多文件输入**                                 | 支持 Excel（.xlsx/.xls）、CSV 或纯文本列表上传                                                    |
| **To/Cc/Bcc 批量发送**                        | 自动从表格提取邮箱并分批（每组50个）发送，支持主送、抄送、密送                                      |
| **自定义 SMTP**                               | 可配置 SMTP_HOST、SMTP_PORT、发件人邮箱及授权密码                                                  |
| **异步并行发送**                               | 高并发发送邮件并实时汇总每次批次的结果                                                              |
| **LLM 驱动报告**                              | 发送完成后，调用 GPT-4o 生成包含成功/失败次数、收件人统计及失败详情的 Markdown 报告                    |
| **前端 & 脚本两种调用**                        | 提供 Dify Workflow (YML)、Flask/API 示例 (`email_app.py`)、命令行脚本 (`main.py`) 等多种集成方式       |

---

## 项目结构 Project Structure

```

email-group-sender-agent/
├── workflows/
│   ├── 测试-Email Group Sender Agent.yml       # 测试版 Workflow&#x20;
│   └── Email Group Sender Agent.yml           # 正式版 Workflow&#x20;
├── tools/
│   ├── bcc\_cc\_emailtool.yaml                  # 群发邮件工具定义&#x20;
│   └── bcc\_cc\_emailtool.py                    # 实现 To/Cc/Bcc 发送逻辑
├── service/
│   ├── email\_app.py                           # Flask HTTP 服务示例
│   ├── task\_app.py                            # 定时/任务触发示例
│   └── main.py                                # 命令行入口脚本
├── utils/
│   ├── process.py                             # Excel/CSV 解析与收件人提取
│   └── bcc\_cc.py                              # 普通批量发送封装函数
├── 163.py                                     # 邮件发送状态回调示例
├── requirements.txt                           # Python 依赖清单
└── README.md                                  # 本文件

````

---

## 安装 Installation

```bash
git clone https://github.com/your-org/email-group-sender-agent.git
cd email-group-sender-agent

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

---

## 使用 Usage

### 1. 通过命令行

```bash
python main.py \
  --excel recipients.xlsx \
  --subject "月度报告" \
  --body "请查收本月度报告。" \
  --smtp_host smtp.example.com \
  --smtp_port 465 \
  --sender sender@example.com \
  --password yourpassword
```

### 2. 通过 Flask 服务

```bash
python email_app.py
# POST http://localhost:5000/send
# Body (JSON):
# {
#   "recipients_file": "path/to/recipients.xlsx",
#   "subject": "...",
#   "body": "...",
#   "smtp_host": "...",
#   "smtp_port": 465,
#   "sender": "...",
#   "password": "..."
# }
```

---

## API 参考 API Reference

### `POST /send`

批量发送邮件并返回统计报告。

* **请求体 Request JSON**

  | 字段                | 类型       | 描述                   |
  | ----------------- | -------- | -------------------- |
  | `recipients_file` | `string` | 收件人 Excel 或 CSV 文件路径 |
  | `subject`         | `string` | 邮件主题                 |
  | `body`            | `string` | 邮件正文（支持 HTML）        |
  | `smtp_host`       | `string` | SMTP 主机地址            |
  | `smtp_port`       | `int`    | SMTP 端口              |
  | `sender`          | `string` | 发件邮箱                 |
  | `password`        | `string` | 发件邮箱密码或授权码           |

* **响应 Response**

  ```json
  {
    "report": "## 邮件发送统计报告\n- 总尝试: ...\n- 成功: ...\n- 失败: ...\n\n### 失败详情\n- ...\n"
  }
  ```

---

## 配置 Configuration

* `bcc_cc_emailtool.yaml`：定义 To/Cc/Bcc 参数及说明
* `Email Group Sender Agent.yml`：Dify Workflow 参数映射
* 环境变量可覆盖 SMTP\_\* 参数

---

## 开发 Development

* **运行单元测试**

  ```bash
  pytest
  ```

* **格式化 & 静态检查**

  ```bash
  black .
  flake8 .
  ```

* **在 Dify 上调试**

  上传 `Email Group Sender Agent.yml` 至 Dify 控制台 → 填写参数 → 运行

---
