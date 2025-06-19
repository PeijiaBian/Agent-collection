````markdown
# 通用 VoC 客户之声智能平台  
# General VoC (Voice of Customer) Intelligence Platform

> 一个通用化的“客户之声”（VoC）多功能智能 Agent 集合  
> A unified suite of intelligent Agents for Voice-of-Customer (VoC) processing and analysis.

---

## 一、项目概览 Project Overview

**中文：**  
本项目整合多种 VoC 与文档处理 Workflow，支持从 Excel/CSV/JSON 中提取用户反馈、自动打标签、可视化展示，并提供文件格式转换、前端 UI 演示等多元化示例。  

**English:**  
This repository combines several VoC and document-processing workflows: extracting user feedback from Excel/CSV/JSON, automated tagging, visualization dashboards, file-format conversion demos, and frontend UI examples.

---

## 二、核心组件 Core Components

| 文件／目录                           | 功能描述（中文）                                    | Description (English)                                    |
|--------------------------------------|----------------------------------------------------|----------------------------------------------------------|
| `通用VoC Agent.yml`                  | 通用 VoC 标签体系工作流（支持“摘要”列，多标签输出）  | Generic VoC tagging workflow (CSV “summary” column, multi-label) :contentReference[oaicite:0]{index=0} |
| `文件转换-demo.yml`                  | Excel 转 JSON 示例 Workflow                          | Demo workflow: Excel → JSON conversion :contentReference[oaicite:1]{index=1} |
| `excel_process.py` / `excel.py`      | Excel 数据读取与预处理脚本                           | Python scripts for reading and preprocessing Excel data |
| `whole.py`                           | 综合调用示例（串联各子模块）                         | Orchestrator script linking all modules                 |
| `download.html` / `example_output.html` | 前端示例：展示输入表单与自动分类结果                  | Frontend demo pages: upload form & auto-tag output  |
| `excel_process.html`                 | 前端示例：Excel 自动处理 & 可视化                    | Frontend demo: Excel processing & visualization :contentReference[oaicite:2]{index=2} |
| `general.html`                       | 通用 VoC 平台首页示例页面                            | Generic VoC platform landing page :contentReference[oaicite:3]{index=3} |
| `vocagent-frontend.html`             | VoC 标签分类专用前端                                 | Dedicated VoC tagging UI :contentReference[oaicite:4]{index=4} |

---

## 三、主要功能 Key Features

1. **多格式输入**  
   - 支持 Excel (`.xlsx`)、CSV、JSON 输入  
   - 支持“摘要”列或纯文本数组     
   **Multi-format Input**  
   - Accepts Excel (`.xlsx`), CSV, JSON arrays of feedback text  

2. **智能标签与分类**  
   - 基于 GPT-4o 的多标签体系生成  
   - “纯消费者声量”(PCD) vs “广告/营销” 等非消费者分类  
   **Smart Tagging & Classification**  
   - GPT-based multi-label tagging  
   - Separates “Pure Consumer Voice” vs “Non-consumer”  

3. **文件转换示例**  
   - Excel → JSON 快速演示  
   **File Conversion Demo**  
   - Excel to JSON conversion workflow  

4. **前端 UI 演示**  
   - 多个静态页面示例 (`download.html`, `excel_process.html` 等)  
   - 支持上传、执行、复制 Markdown & 下载结果  
   **Frontend Demos**  
   - Static HTML pages for upload, run, copy Markdown & download results  

5. **可视化与仪表盘**  
   - 标签分类结果表格、饼图、词云等  
   **Visualization & Dashboard**  
   - Tables, charts, word-clouds of tagging results  

6. **脚本与编程接口**  
   - `excel_process.py`、`whole.py` etc. 可单独调用  
   **Scripts & API**  
   - Modular Python scripts for programmatic integration  

---

## 四、快速开始 Quick Start

1. **克隆仓库 / Clone**

   ```bash
   git clone https://github.com/your-org/general-voc-platform.git
   cd general-voc-platform
````

2. **安装依赖 / Install Dependencies**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **运行示例 / Run Demos**

   * **Excel→JSON 转换**

     ```bash
     kofe excel2json --excel_path path/to/data.xlsx
     ```
   * **前端演示**
     直接打开浏览器访问 `download.html` / `example_output.html` / `excel_process.html` / `general.html` / `vocagent-frontend.html`

   **File Conversion**

   ```bash
   fft run 文件转换-demo.yml
   ```

---