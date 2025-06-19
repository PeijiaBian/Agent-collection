from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import uuid4
from datetime import datetime
import asyncio
import requests

app = FastAPI()

# 模拟数据库，实际可换为 MongoDB / PostgreSQL
tasks_db: Dict[str, dict] = {}

# ===== 输入模型 =====
class MessageInput(BaseModel):
    message_id: str
    item: int  # message_id 对应的邮件数量

class TaskCreateRequest(BaseModel):
    user_id: str
    messages: List[MessageInput]  # 每次只传一个 message_id

# ===== 输出模型 =====
class TaskStatus(BaseModel):
    task_id: str
    message_id: str
    total_expected: int
    total: int
    success: int
    failure: int
    completed: bool
    result_data: Optional[dict] = None  # 保存 email-status 接口返回

# ===== 创建任务接口 =====
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

    # 启动异步后台轮询
    asyncio.create_task(poll_status(task_id))
    return {"task_id": task_id}

# ===== 后台轮询函数（每3分钟查一次）=====
async def poll_status(task_id: str):
    while True:
        await asyncio.sleep(180)  # 每3分钟轮询一次

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
                task["result_data"] = data  # 保存完整结果
                break
        except Exception as e:
            print(f"轮询失败 message_id: {task['message_id']} 错误: {e}")

# ===== 查询单个任务状态 =====
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

# ===== 查询某用户的所有任务 =====
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
