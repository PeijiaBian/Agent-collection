import asyncio
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests
import re
import json
import uvicorn
import time
import cv2
import numpy as np
import base64
from typing import Callable, List
import os
from tempfile import NamedTemporaryFile
from speech_flow import create, query  # 导入speech-flow.py中的函数
import logging

from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

from googleapiclient.discovery import build
from youtube_transcript_api._errors import TranscriptsDisabled

# 配置logging，添加更详细的格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 获取logger实例
logger = logging.getLogger(__name__)

os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"

app = FastAPI()


class InputText(BaseModel):
    text: str


def get_video_id(url):
    # 首先检查是否是长链接
    long_url_match = re.search(r'video/(\d+)', url)
    if long_url_match:
        return long_url_match.group(1)
    
    # 如果是短链接，则进行重定向获取长链接
    try:
        response = requests.get(url, allow_redirects=True)
        final_url = response.url
        match = re.search(r'video/(\d+)', final_url)
        return match.group(1) if match else None
    except Exception as e:
        logger.error(f"获取视频ID失败: {str(e)}")
        return None


def get_video_info(video_id):
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'referer': 'https://www.douyin.com/?is_from_mobile_home=1&recommend=1'
    }
    url = f'https://www.iesdouyin.com/share/video/{video_id}/'
    res = requests.get(url, headers=headers).text
    try:
        data = re.findall(r'_ROUTER_DATA\s*=\s*(\{.*?\});', res)[0]
        json_data = json.loads(data)
        item_list = json_data['loaderData']['video_(id)/page']['videoInfoRes']['item_list'][0]
        video = item_list['video']['play_addr']['uri']
        video_url = f'https://www.douyin.com/aweme/v1/play/?video_id={video}' if 'mp3' not in video else video
        return video_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取视频信息失败: {str(e)}")


@app.post("/get_video_url")
def get_video_url(input_data: InputText):
    logger.info(f"开始获取视频URL, input --> : {input_data.text}")
    # 同时匹配短链接和长链接
    short_url_match = re.search(r'https://v\.douyin\.com/\S+', input_data.text)
    long_url_match = re.search(r'https://www\.douyin\.com/video/\d+', input_data.text)
    
    if not (short_url_match or long_url_match):
        raise HTTPException(status_code=400, detail="未找到有效的抖音链接")
    
    # 使用匹配到的URL
    url = short_url_match.group(0) if short_url_match else long_url_match.group(0)
    
    video_id = get_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="无法提取视频ID")
    
    video_url = get_video_info(video_id)
    logger.info(f"获取视频URL结束, result --> {video_url}")
    return {"video_url": video_url}


# 添加新的请求模型
class VideoTranscriptRequest(BaseModel):
    text: str


# 添加新的接口
@app.post("/get_video_transcript")
def get_video_transcript(request: VideoTranscriptRequest):
    try:
        # 1. 获取视频URL
        video_url_response = get_video_url(InputText(text=request.text))
        video_url = video_url_response["video_url"]

        # 2. 创建转写任务
        task_id = create(video_url)
        if not task_id:
            raise HTTPException(status_code=500, detail="创建转写任务失败")

        # 3. 查询转写结果并解析
        try:
            transcript_result = query(task_id)
            if transcript_result.get("code") == 11000:
                result_json = json.loads(transcript_result["result"])
                
                 # 提取sentences并去掉words属性
                cleaned_sentences = []
                for sentence in result_json['sentences']:
                    cleaned_sentence = {
                        "bt": sentence['bt'],
                        "et": sentence['et'],
                        "s": sentence['s']
                    }
                    cleaned_sentences.append(cleaned_sentence)
                    

                return {
                    "success": True,
                    "text": cleaned_sentences,
                    "url": video_url
                }
            else:
                raise HTTPException(status_code=500, detail=f"转写失败: {transcript_result.get('msg', '未知错误')}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"解析转写结果失败: {str(e)}")

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")


# xhs视频处理部分代码
# 提取中间字符串的工具函数
def get_mid_string(html, start_str, end_str):
    try:
        start = html.find(start_str)
        if start >= 0:
            start += len(start_str)
            end = html.find(end_str, start)
            if end >= 0:
                return html[start:end].strip()
    except:
        pass
    return None

# 提取URL的函数
def extract_url(text):
    # 优化后的正则表达式，支持提取特殊字符的URL
    urls = re.findall(r'http[s]?://[a-zA-Z0-9./?=&-_]+', text)
    if urls:
        return urls[0]
    else:
        return None

# 获取真实视频URL的函数
def get_real_video_url(text: str) -> str:
    url = extract_url(text)
    if not url:
        return "未找到有效的URL"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            page_content = response.text
        elif response.status_code // 100 == 3:
            redirect_url = response.headers.get('Location')
            response = requests.get(redirect_url, timeout=10)
            if response.status_code == 200:
                page_content = response.text
            else:
                return "无法获取最终页面"
        else:
            return "请求失败，状态码: {}".format(response.status_code)

        # 提取视频URL
        video = get_mid_string(page_content, '"masterUrl":"', '","')
        if not video:
            return "无法提取视频链接"

        # 处理视频URL中的特殊字符
        video_url = video.replace("\\u002F", "/")
        return video_url

    except requests.exceptions.RequestException as e:
        return "网络请求错误: {}".format(str(e))
    except Exception as e:
        return str(e)

# 添加新的小红书视频接口
@app.post("/get_xhs_video_transcript")
def get_video_transcript(request: InputText):
    try:
        # 1. 获取视频URL
        # video_url_response = get_video_url(InputText(text=request.text))
        # video_url = video_url_response["video_url"]
        video_url = get_real_video_url(request.text)
        # 2. 创建转写任务
        task_id = create(video_url)
        if not task_id:
            raise HTTPException(status_code=500, detail="创建转写任务失败")

        # 3. 查询转写结果并解析
        try:
            transcript_result = query(task_id)
            if transcript_result.get("code") == 11000:
                result_json = json.loads(transcript_result["result"])
                
                 # 提取sentences并去掉words属性
                cleaned_sentences = []
                for sentence in result_json['sentences']:
                    cleaned_sentence = {
                        "bt": sentence['bt'],
                        "et": sentence['et'],
                        "s": sentence['s']
                    }
                    cleaned_sentences.append(cleaned_sentence)
                    

                return {
                    "success": True,
                    "text": cleaned_sentences,
                    "url": video_url
                }
            else:
                raise HTTPException(status_code=500, detail=f"转写失败: {transcript_result.get('msg', '未知错误')}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"解析转写结果失败: {str(e)}")

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")
    
# 添加新的YouTube视频接口
@app.post("/get_ytb_video_transcript")
def get_video_transcript(request: InputText):
    try:
        # 获取视频URL或直接视频ID
        video_url = request.text
        if "youtube.com" in video_url or "youtu.be" in video_url:
            # 使用 pytube 获取视频ID
            yt = YouTube(video_url)
            video_id = yt.video_id
        else:
            # 如果输入的是视频ID
            video_id = video_url

        # 获取视频转录
        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=['zh-Hans'], proxies={"http": "http://api.wlai.vip"}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取转录失败: {str(e)}")

        # 解析转录结果
        cleaned_sentences = []
        for entry in transcript:
            start_time = entry['start']
            duration = entry['duration']
            end_time = start_time + duration

            # 构造符合要求的格式
            cleaned_sentences.append({
                "bt": round(start_time, 2),  # 开始时间
                "et": round(end_time, 2),   # 结束时间
                "s": entry['text']          # 转录内容
            })

        # 返回结果
        return {
            "success": True,
            "text": cleaned_sentences,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")
    
# kuaishou尝试
# 添加新的接口
@app.post("/get_video_transcript")
def get_video_transcript(request: VideoTranscriptRequest):
    try:
        # 1. 获取视频URL
        video_url_response = get_video_url(InputText(text=request.text))
        video_url = video_url_response["video_url"]

        # 2. 创建转写任务
        task_id = create(video_url)
        if not task_id:
            raise HTTPException(status_code=500, detail="创建转写任务失败")

        # 3. 查询转写结果并解析
        try:
            transcript_result = query(task_id)
            if transcript_result.get("code") == 11000:
                result_json = json.loads(transcript_result["result"])
                
                 # 提取sentences并去掉words属性
                cleaned_sentences = []
                for sentence in result_json['sentences']:
                    cleaned_sentence = {
                        "bt": sentence['bt'],
                        "et": sentence['et'],
                        "s": sentence['s']
                    }
                    cleaned_sentences.append(cleaned_sentence)
                    

                return {
                    "success": True,
                    "text": cleaned_sentences,
                    "url": video_url
                }
            else:
                raise HTTPException(status_code=500, detail=f"转写失败: {transcript_result.get('msg', '未知错误')}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"解析转写结果失败: {str(e)}")

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")



# 添加新的请求模型
class Sentence(BaseModel):
    bt: int
    et: int
    s: str
    logic: str
    link: str 

class VideoFrameRequest(BaseModel):
    sentences: List[Sentence]
    url: str
    summary: str
    content: str
    
# 添加新的工具函数
def download_video(url: str) -> str:
    """下载视频到临时文件并返回文件路径"""
    try:
       
        
        # 创建临时文件
        temp_file = NamedTemporaryFile(delete=False, suffix='.mp4')
        
        # 下载视频
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 写入临时文件
        with open(temp_file.name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return temp_file.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载视频失败: {str(e)}")

def get_frame_at_time(video_path: str, timestamp_ms: int) -> str:
    """从视频指定时间获取帧并转换为base64字符串"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("无法打开视频文件")
            
        # 将毫秒转换为秒
        timestamp_sec = timestamp_ms / 1000
        
        # 设置视频位置
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
        
        # 读取帧
        ret, frame = cap.read()
        if not ret:
            raise Exception("无法读取视频帧")
            
        # 压缩图片
        # 1. 调整图片大小
        max_size = 400  # 最大边长为800像素
        height, width = frame.shape[:2]
        if width > max_size or height > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
        # 2. JPEG压缩
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 40]  # 设置JPEG质量为60%
        _, buffer = cv2.imencode('.jpg', frame, encode_param)
        
        # 转换为base64并进行URL安全编码
        base64_image = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')
        
        cap.release()
        logger.info(f"压缩后的图片大小: {len(base64_image) / 1024:.2f}KB")
        return base64_image
    except Exception as e:
        logger.error(f"获取视频帧失败: {str(e)}", exc_info=True)
        raise Exception(f"获取视频帧失败: {str(e)}")

# 添加新的接口
@app.post("/get_video_frames")
def get_video_frames(request: VideoFrameRequest):
    try:
        logger.info(f"开始处理视频帧请求: url={request.url}, sentences数量={len(request.sentences)}")
        
        # 下载视频
        logger.info("开始下载视频...")
        video_path = download_video(request.url)
        logger.info(f"视频下载完成，临时文件路径: {video_path}")
        
        try:
            # 处理每个句子，添加对应时间点的图片
            result = []
            for index, sentence in enumerate(request.sentences, 1):
                logger.info(f"处理第{index}个句子: 时间戳={sentence.et}ms, 开始时间={sentence.bt}ms")
                try:
                    # 使用句子的中间时间获取帧
                    frame_time = (sentence.et + sentence.bt) / 2
                    frame_base64 = get_frame_at_time(video_path, frame_time)
                    logger.info(f"成功获取第{index}个句子的视频帧，时间点={frame_time}ms")
                    
                    # 将Pydantic模型转换为字典，然后添加image属性
                    sentence_data = sentence.dict()
                    sentence_data["image"] = frame_base64
                    result.append(sentence_data)
                except Exception as e:
                    logger.error(f"处理第{index}个句子失败: {str(e)}", exc_info=True)
                    # 如果单个句子处理失败，添加没有图片的句子数据
                    sentence_data = sentence.dict()
                    sentence_data["image"] = None
                    sentence_data["error"] = str(e)
                    result.append(sentence_data)
                    
        finally:
            # 清理临时文件
            try:
                logger.info("清理临时文件...")
                os.unlink(video_path)
                logger.info("临时文件清理完成")
            except Exception as e:
                logger.error(f"清理临时文件失败: {str(e)}", exc_info=True)
                
        
        res = {
            "success": True,
            "sentences": result
        }
        # logger.info(f"视频帧处理完成,response: {res}")
        return res
        
    except Exception as e:
        logger.error(f"处理视频帧失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理视频帧失败: {str(e)}")



# youtube transcript and comments analysis
def cached_get_video_info(api_key, video_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(part="snippet,statistics", id=video_id)
    response = request.execute()
    return response

def cached_get_comment_threads(api_key, video_id, max_results=100):
    youtube = build("youtube", "v3", developerKey=api_key)
    return youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        textFormat="plainText"
    ).execute()

def extract_video_id(url):
    """
    从 YouTube URL 中提取视频ID
    """
    video_id_match = re.search(r'(?:v=|/)([\w-]{11})(?:\?|&|/|$)', url)
    if video_id_match:
        return video_id_match.group(1)
    return None

def format_comments(comments):
    """
    格式化评论文本
    """
    if isinstance(comments, str):
        return comments
    formatted_text = ""
    for idx, comment in enumerate(comments, 1):
        formatted_text += (
            f"评论 {idx}:\n{comment['text']}\n"
            f"发布时间: {comment['publishedAt']}\n"
            f"点赞数: {comment['likes']}\n\n"
        )
    return formatted_text


# 配置日志
logging.basicConfig(level=logging.INFO, filename="server.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

@app.post("/youtube_analysis_api")
def fetch_video_data(request: InputText):
    """
    使用输入的 URL 或视频 ID 获取视频信息、字幕和评论，并返回结果。
    """
    try:
        # 获取视频URL或视频ID
        video_input = request.text
        if "youtube.com" in video_input or "youtu.be" in video_input:
            yt = YouTube(video_input)
            video_id = yt.video_id
            video_url = video_input
        else:
            video_id = video_input
            video_url = f"https://www.youtube.com/watch?v={video_id}"

        logging.info(f"解析到的视频ID: {video_id}")

        youtube_api_key = "AIzaSyCOs0X0-EMnF-kgfhn53lyXLlgcXBUQKa0"

        # 获取视频信息
        logging.info("正在获取视频信息...")
        try:
            video_response = cached_get_video_info(youtube_api_key, video_id)
            if not video_response.get("items"):
                error_msg = "未找到视频信息"
                logging.error(error_msg)
                return {"success": False, "error": error_msg}
        except requests.exceptions.Timeout:
            error_msg = "获取视频信息超时"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}
        
        video_info = video_response["items"][0]
        video_title = video_info["snippet"]["title"]
        view_count = video_info["statistics"].get("viewCount", "0")
        like_count = video_info["statistics"].get("likeCount", "0")
        comment_count = video_info["statistics"].get("commentCount", "0")

        # proxies = {
        #     "http": "http://127.0.0.1:7890",
        #     "https": "http://127.0.0.1:7890"
        # }
        
        # 获取字幕
        logging.info("正在获取字幕...")
        transcript_text = ""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = None
            try:
                transcript = transcript_list.find_generated_transcript(["zh-Hans", "zh-CN", "en"])
            except Exception as e:
                logging.warning(f"未找到自动生成的字幕，尝试获取手动字幕: {str(e)}")
                transcript = transcript_list.find_manually_created_transcript(["zh-Hans", "zh-CN", "en"])

            transcript_text = " ".join([item["text"] for item in transcript.fetch()])
            logging.info("成功获取字幕")
        except TranscriptsDisabled:
            transcript_text = "字幕不可用（视频禁止字幕）"
            logging.warning(transcript_text)
        except requests.exceptions.Timeout:
            error_msg = "获取字幕超时"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"获取字幕出错: {str(e)}"
            logging.error(error_msg)
            transcript_text = error_msg

        # 获取评论
        logging.info("正在获取评论...")
        comments_text = ""
        try:
            comments_data = cached_get_comment_threads(youtube_api_key, video_id, max_results=100)
            comments = []
            for item in comments_data.get("items", []):
                comment_snippet = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "text": comment_snippet["textDisplay"],
                    "publishedAt": comment_snippet["publishedAt"],
                    "likes": comment_snippet["likeCount"]
                })
            comments_text = format_comments(comments)
            logging.info("成功获取评论")
        except requests.exceptions.Timeout:
            error_msg = "获取评论超时"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"获取评论出错: {str(e)}"
            logging.error(error_msg)
            comments_text = error_msg

        # 返回结果
        result = {
            "success": True,
            "video_info": {
                "video_title": video_title,
                "view_count": view_count,
                "like_count": like_count,
                "comment_count": comment_count
            },
            "transcript_text": transcript_text,
            "comments_text": comments_text,
            "url": video_url
        }

        logging.info(f"API调用成功，返回结果: {result}")
        return result

    except Exception as e:
        error_msg = f"处理请求时出错: {str(e)}"
        logging.error(error_msg)
        return {"success": False, "error": error_msg}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)