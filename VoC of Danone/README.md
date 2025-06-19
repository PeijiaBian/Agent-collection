# 达能客户声音（VoC）负面情绪标签 Agent

> 一个面向达能（Danone）品牌的“客户声音”（Voice of Customer, VoC）微服务  
> 自动从用户评论或反馈文本中识别负面情绪打分、分类并可视化展示。

---

## 一、项目简介

**中文：**  
VoC of Danone Agent 针对达能产品的用户评论或反馈，自动完成以下任务：  
1. **提取文本内容** — 支持 CSV 和 JSON 两种输入格式；  
2. **识别负面情绪** — 判断文本是否包含负面含义；  
3. **负面打分与原因分析** — 0–100 分量化负面强度，并输出简要原因；  
4. **纯消费者声量分类** — 区分“纯消费者声量”（PCD）与“非消费者声量”；  
5. **可视化展示** — 前端与 Streamlit 两种界面，实时查看分析结果。

**English (for reference)：**  
VoC of Danone Agent automatically ingests user feedback (CSV or JSON), detects negative sentiment, scores intensity (0–100), summarizes reasons, classifies pure consumer voice vs. others, and provides both frontend and Streamlit visualizations.

---

## 二、主要功能

| 功能                         | 说明                                                              |
|------------------------------|-------------------------------------------------------------------|
| 多格式输入                    | 支持上传 CSV (`“文本内容”` 列) 或 JSON 数组格式的用户文本          |
| 负面情绪识别                  | 基于上下文判断是否存在负面情绪（抱怨、不满、问题等）              |
| 量化评分与原因归纳            | `score`（0-100 整数）定量负面程度，`reason` 简要总结核心负面原因  |
| 纯消费者声量 vs. 非消费者声量 | 将“纯消费者声量”（PCD）与广告/科普/营销等“remove”分类分开输出     |
| 前端演示（Flask/JS）          | `达能前端.py` 提供 REST API 及静态页面示例                         |
| Streamlit 可视化             | `达能streamlit.py` 一键启动交互式仪表盘                           |

---

## 三、目录结构

```

voc-danone-agent/
├── frontend/
│   └── 达能前端.py         # Flask + JavaScript 简易 UI
├── streamlit/
│   └── 达能streamlit.py   # Streamlit 可视化应用
├── workflows/
│   ├── 达能-负面情绪标签-csv文本版本.yml
│   └── 达能-负面情绪标签-json输入版本.yml
├── requirements.txt        # Python 依赖
└── README.md               # 本文件

```

---

## 四、安装与依赖

1. **克隆代码库**  
   ```bash
   git clone https://github.com/agent-collection/voc-danone-agent.git
   cd voc-danone-agent
    ```

2. **创建并激活虚拟环境**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

---

## 五、快速启动

### 5.1 前端演示（Flask）

```bash
cd frontend
python 达能前端.py
```

* 默认监听 `http://localhost:5000`
* 上传 CSV/JSON 文本文件后点击“分析”按钮，即可查看打分与分类结果。

### 5.2 Streamlit 可视化

```bash
cd streamlit
streamlit run 达能streamlit.py
```

* 打开浏览器访问 `http://localhost:8501`
* 支持粘贴 JSON 数组或上传 CSV，右侧实时展示情绪评分、分类饼图与原因云图。

---

## 六、使用说明

1. **CSV 输入**

   * 文件第一列须为 `文本内容`，每行一条用户评论。
2. **JSON 输入**

   * 须为纯文本数组 `["评论1", "评论2", …]`。
3. **模型推理与分类**

   * 依据 workflow 中定义的 GPT-4o 提示词，逐条输出：

     ```json
     [
       { "text": "…", "score": 75, "reason": "价格高、体验差" },
       { "text": "…", "score": 0,  "reason": "无负面含义" }
     ]
     ```
   * 同时将纯消费者声量（PCD）与其他（remove）分别输出到两个列表。

---

## 七、示例演示

* **示例 CSV**:

  ```csv
  文本内容
  这款酸奶太酸，喝不下去。
  包装很好，口味也不错。
  ```

* **示例 JSON**:

  ```json
  ["酸奶味道太浓，喝完胃不舒服。", "送货速度很快，很赞！"]
  ```

* **期望输出（JSON）**:

  ```json
  [
    { "text": "这款酸奶太酸，喝不下去。", "score": 80, "reason": "口味过酸、体验极差" },
    { "text": "包装很好，口味也不错。", "score": 0,  "reason": "无负面含义" }
  ]
  ```

---

## 八、更多配置

* 修改 `workflows/…yml` 可自定义提示词和模型参数
* 前端可替换为任意 Flask/React/UI 框架
* Streamlit 脚本中可添加更多可视化组件

---

