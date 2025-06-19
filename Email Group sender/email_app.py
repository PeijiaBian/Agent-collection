from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
import re

app = FastAPI()

class TableText(BaseModel):
    text: str

def extract_emails_from_markdown(md_text: str) -> List[str]:
    # 去掉前后可能的 {{ 和 }} 包裹
    if md_text.startswith("{{") and md_text.endswith("}}"):
        md_text = md_text[2:-2].strip()

    # 继续原来的处理流程
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

    for line in lines[2:]:  # 跳过表头和分隔行
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
