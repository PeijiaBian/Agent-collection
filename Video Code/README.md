# Speech Flow Web API   短视频与 YouTube 转录与评论抓取服务

---

## 简介 Introduction

**中文：**  
Speech Flow Web API 是一个基于 FastAPI 的轻量级微服务，支持抖音/快手短视频及 YouTube 视频的转录与评论抓取。它自动提取视频 ID、调用外部转录接口或 YouTubeTranscriptApi，返回结构化的字幕数据与视频元信息。

**English:**  
Speech Flow Web API is a lightweight FastAPI microservice that transcribes Douyin/Kuaishou short videos and YouTube videos, and fetches comments. It automatically parses video IDs, calls external transcription services or YouTubeTranscriptApi, and returns structured transcript data alongside video metadata.

---

## 主要功能 Features

- **抖音/快手视频转写**  
  - 自动解析分享链接或短链接，获取真实播放地址  
  - 调用外部转写服务输出带时间戳的字幕  
  - 返回 `success`, `text`（[{bt, et, s} 列表）和 `url`

- **YouTube 转录与评论抓取**  
  - 支持 URL 或视频 ID 输入  
  - 使用 YouTubeTranscriptApi 获取字幕文本  
  - 抓取视频标题、播放量、点赞数、评论数  
  - 返回 `video_info`, `transcript_text`, `comments_text`, `url`

- **高可用与稳健**  
  - 异常捕获、超时重试  
  - 详尽日志记录（时间、级别、文件与行号）  
  - 可配置 HTTP/HTTPS 代理

---

## 项目结构 Project Structure

```

├── speech\_flow\.py       # 转写任务逻辑（创建与查询）
├── webapp.py            # FastAPI 应用与路由定义&#x20;
├── requirements.txt     # Python 依赖列表&#x20;
├── run\_webapp.sh        # 启动脚本，后台运行并输出日志&#x20;
└── app.log              # 默认日志输出文件

````

---

## 安装与运行 Installation & Run

1. **安装依赖 Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

2. **配置代理（可选） Configure proxy (optional)**

   ```bash
   export http_proxy="http://127.0.0.1:7890"
   export https_proxy="http://127.0.0.1:7890"
   ```
3. **启动服务 Start service**

   ```bash
   bash run_webapp.sh
   ```
4. **访问 Address**
   默认监听 `0.0.0.0:8080`

---

## API 接口 API Endpoints

### 1. `POST /get_video_transcript`

**功能 Function:** 转写抖音/快手视频
**Request Body：**

```json
{ "text": "<抖音/快手分享链接或视频URL>" }
```

**成功 Success Response：**

```json
{
  "success": true,
  "text": [
    { "bt": 0.00, "et": 3.20, "s": "第一个句子内容" },
    …
  ],
  "url": "<实际播放地址>"
}
```

**失败 Error Response：**

```json
{ "success": false, "error": "<错误消息>" }
```

### 2. `POST /get_ytb_video_transcript`

**功能 Function:** 转写 YouTube 并抓取评论
**Request Body：**

```json
{ "text": "<YouTube URL 或 视频ID>" }
```

**Success Response：**

```json
{
  "video_info": {
    "video_title": "...",
    "view_count": 123456,
    "like_count": 7890,
    "comment_count": 321
  },
  "transcript_text": [ { "start": 0.0, "text": "..." }, … ],
  "comments_text": [ "评论1", "评论2", … ],
  "url": "https://www.youtube.com/watch?v=<ID>"
}
```

---

## 配置 Configuration

* **代理 Proxy:**
  通过环境变量 `http_proxy` / `https_proxy` 配置网络请求代理。
* **日志 Logging:**
  在 `run_webapp.sh` 中可修改日志文件路径或级别。

---

## 依赖 Requirements

```text
fastapi==0.68.0
uvicorn==0.15.0
pydantic==1.8.2
requests==2.26.0
opencv-python
numpy
youtube-transcript-api==0.6.3
pytube==15.0.0
google-api-python-client==2.158.0
```
---

## 展望 Future Work

* 支持更多视频平台（B 站、Twitter）
* 接入多语言转写模型
* 提供 Web 前端和仪表盘

---

