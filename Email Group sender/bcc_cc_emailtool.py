import json
import uuid
from typing import Any, Union

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool


class EmailTool(BuiltinTool):
    def _invoke(self,
                user_id: str,
                tool_parameters: dict[str, Any],
                ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
        Main callable method for the tool from Dify
        """
        # 获取必要参数
        to_list_str = tool_parameters.get('receiver_email', '')
        to_list = [email.strip() for email in to_list_str.split(',')] if to_list_str else []

        subject = tool_parameters.get('subject', '')
        text = tool_parameters.get('text', '')
        if not text:
            return self.create_text_message('Invalid parameter: text')

        sender_email = tool_parameters.get('sender_email', 'agent@iagent.cc')
        password = tool_parameters.get('password', 'uB?Zw6ZbW3')
        smtp_host = tool_parameters.get('SMTP_HOST', '101.89.86.84')
        smtp_port = int(tool_parameters.get('SMTP_PORT', '465'))

        # 解析 cc 和 bcc 字符串
        cc_list_str = tool_parameters.get('cc_list', '')
        cc_list = [email.strip() for email in cc_list_str.split(',')] if cc_list_str else []

        bcc_list_str = tool_parameters.get('bcc_list', '')
        bcc_list = [email.strip() for email in bcc_list_str.split(',')] if bcc_list_str else []

        try:
            result = self._send_email(to_list, subject, text,
                                      sender_email, password, smtp_host, smtp_port,
                                      cc_list, bcc_list)
            return self.create_text_message(json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as e:
            return self.create_text_message(f'Failed to send email: {str(e)}')

    def _send_email(self,
                    to_list: list[str],
                    subject: str,
                    html_text: str,
                    sender_email: str,
                    password: str,
                    smtp_host: str,
                    smtp_port: int,
                    cc_list: list[str] = [],
                    bcc_list: list[str] = []) -> dict:

        # 手动生成符合 RFC 标准的 Message-ID
        domain = sender_email.split('@')[-1]
        msg_uid = uuid.uuid4().hex
        msg_id = f"<{msg_uid}@{domain}>"

        message = MIMEMultipart()
        message["From"] = sender_email
        if to_list:
            message["To"] = ", ".join(to_list)
        if cc_list:
            message["Cc"] = ", ".join(cc_list)
        message["Subject"] = Header(subject, 'utf-8')
        message["Message-ID"] = msg_id  # 手动设置 Message-ID
        message["Date"] = formatdate(localtime=True)

        message.attach(MIMEText(html_text, "html", "utf-8"))

        all_recipients = to_list + cc_list + bcc_list
        if not all_recipients:
            return {"code": "0", "error": "❌ 错误：至少需要一个收件人（To / Cc / Bcc）"}

        server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        server.login(sender_email, password)
        server.sendmail(sender_email, all_recipients, message.as_string())
        server.quit()

        return {
            "code": "1",
            "to": to_list,
            "cc": cc_list,
            "bcc": bcc_list,
            "message_id": msg_id
        }
