import json
from typing import Any, Union

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
        receiver_email = tool_parameters.get('receiver_email', '')
        if not receiver_email:
            return self.create_text_message('Invalid parameter: receiver_email')

        subject = tool_parameters.get('subject', '')
        text = tool_parameters.get('text', '')
        if not text:
            return self.create_text_message('Invalid parameter: text')

        sender_email = tool_parameters.get('sender_email', 'lightark1@163.com')
        password = tool_parameters.get('password', 'XVYTCGILLSKVUSQN')
        SMTP_HOST = tool_parameters.get('SMTP_HOST', 'smtp.163.com')
        SMTP_PORT = tool_parameters.get('SMTP_PORT', '465')

        # 获取 BCC 列表（注意现在是字符串，逗号分隔）
        bcc_list_str = tool_parameters.get('bcc_list', '')
        bcc_list = [email.strip() for email in bcc_list_str.split(',')] if bcc_list_str else []

        try:
            result = self._extract(receiver_email, subject, text,
                                   sender_email, password, SMTP_HOST, SMTP_PORT, bcc_list)
            return self.create_text_message(str(result))
        except Exception as e:
            return self.create_text_message(f'Failed to send email: {str(e)}')

    def _extract(self,
                 receiver_email: str,
                 subject: str,
                 text: str,
                 sender_email: str,
                 password: str,
                 SMTP_HOST: str,
                 SMTP_PORT: str,
                 bcc_list: list[str] = []) -> str:
        # 构建邮件
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(text, "html"))  # 支持HTML格式正文

        # 全部接收者（收件人 + 隐藏抄送）
        all_recipients = [receiver_email] + bcc_list

        # 连接SMTP服务器并发送邮件
        server = smtplib.SMTP_SSL(SMTP_HOST, int(SMTP_PORT))
        server.login(sender_email, password)
        server.sendmail(sender_email, all_recipients, message.as_string())
        server.quit()

        return {"code": "1"}  # 成功


# ✅ 本地调试用
if __name__ == '__main__':
    tool = EmailTool()

    # 测试用例，逗号分隔
    bcc_emails = "bianpj18@163.com,bianpj2023@163.com"

    # 发送测试
    print(tool._extract(
        receiver_email='agent@iagent.cc',
        subject='测试邮件 - 含BCC',
        text='<h3>你好，这是一个测试邮件，包含 BCC 收件人</h3>',
        sender_email='agent@iagent.cc',
        password='uB?Zw6ZbW3',
        SMTP_HOST='101.89.86.84',
        SMTP_PORT='465',
        bcc_list=[email.strip() for email in bcc_emails.split(',')]
    ))
