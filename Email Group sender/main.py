from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import uuid4
from datetime import datetime
import asyncio
import requests
import re

app = FastAPI()

# ====================== 模拟数据库 ======================
tasks_db: Dict[str, dict] = {}

# ====================== 邮件任务模块 ======================
class MessageInput(BaseModel):
    message_id: str
    item: int

class TaskCreateRequest(BaseModel):
    user_id: str
    messages: List[MessageInput]

class TaskStatus(BaseModel):
    task_id: str
    message_id: str
    total_expected: int
    total: int
    success: int
    failure: int
    completed: bool
    result_data: Optional[dict] = None

@app.post("/task/create")
async def create_task(request: TaskCreateRequest):
    if len(request.messages) != 1:
        raise HTTPException(status_code=400, detail="Only one message_id allowed per request.")

    msg = request.messages[0]
    task_id = str(uuid4())

    tasks_db[task_id] = {
        "user_id": request.user_id,
        "message_id": msg.message_id,
        "total_expected": msg.item,
        "status": {
            "total": 0,
            "success": 0,
            "failure": 0,
            "completed": False
        },
        "result_data": None,
        "created_at": datetime.utcnow()
    }

    asyncio.create_task(poll_status(task_id))
    return {"task_id": task_id}

async def poll_status(task_id: str):
    while True:
        await asyncio.sleep(60) #等待时间

        task = tasks_db.get(task_id)
        if not task:
            return

        try:
            res = requests.post("https://www.iagent.cc/email-status", json={"message_id": task["message_id"]})
            data = res.json()

            task["status"]["total"] = data.get("total", 0)
            task["status"]["success"] = data.get("success", 0)
            task["status"]["failure"] = data.get("failure", 0)

            if task["status"]["total"] >= task["total_expected"]:
                task["status"]["completed"] = True
                task["result_data"] = data
                break
        except Exception as e:
            print(f"轮询失败 message_id: {task['message_id']} 错误: {e}")

@app.get("/task/status/{task_id}", response_model=TaskStatus)
def get_status(task_id: str):
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatus(
        task_id=task_id,
        message_id=task["message_id"],
        total_expected=task["total_expected"],
        result_data=task.get("result_data"),
        **task["status"]
    )

@app.get("/task/user/{user_id}")
def get_user_tasks(user_id: str):
    return {
        "tasks": [
            {
                "task_id": task_id,
                "message_id": task["message_id"],
                "total_expected": task["total_expected"],
                "result_data": task.get("result_data"),
                **task["status"]
            }
            for task_id, task in tasks_db.items()
            if task["user_id"] == user_id
        ]
    }

# ====================== 表格邮箱提取模块 ======================
class TableText(BaseModel):
    text: str

def extract_emails_from_markdown(md_text: str) -> List[str]:
    if md_text.startswith("{{") and md_text.endswith("}}"):
        md_text = md_text[2:-2].strip()

    lines = md_text.strip().splitlines()
    if len(lines) < 2:
        return []

    headers = [col.strip() for col in lines[0].strip('|').split('|')]
    email_index = None

    for i, h in enumerate(headers):
        if '邮箱' in h or 'email' in h.lower():
            email_index = i
            break

    if email_index is None:
        return []

    seen = set()
    unique_emails = []

    for line in lines[2:]:
        cols = [col.strip() for col in line.strip('|').split('|')]
        if len(cols) > email_index:
            email = cols[email_index]
            if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                if email not in seen:
                    seen.add(email)
                    unique_emails.append(email)

    result = []
    for i in range(0, len(unique_emails), 50):
        group = unique_emails[i:i + 50]
        result.append(",".join(group))

    return result

@app.post("/extract-emails", response_model=List[str])
async def extract_emails(input_data: TableText):
    return extract_emails_from_markdown(input_data.text)
