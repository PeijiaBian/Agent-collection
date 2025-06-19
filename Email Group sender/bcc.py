import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header


def send_email(
    receiver_email: str,
    subject: str,
    html_text: str,
    sender_email: str,
    password: str,
    smtp_host: str = 'smtp.163.com',
    smtp_port: int = 465,
    bcc_list: list[str] = []
) -> str:
    # 构建邮件对象
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = Header(subject, 'utf-8') 
    message.attach(MIMEText(html_text, "html", "utf-8"))

    # 所有接收人：To + BCC
    all_recipients = [receiver_email] + bcc_list

    # 启动SMTP连接并发送邮件
    try:
        server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        server.login(sender_email, password)
        server.sendmail(sender_email, all_recipients, message.as_string())
        server.quit()
        return "✅ 邮件发送成功"
    except Exception as e:
        return f"❌ 邮件发送失败：{str(e)}"


# ✅ 测试用例（直接运行该文件会执行这个）
if __name__ == "__main__":
    # 收件人
    to_email = "agent@iagent.cc"

    # 隐藏抄送（群发）
    bcc_emails = ["bianpj18@163.com","bianpj2023@163.com"]

    # 发件人配置
    sender = "agent@iagent.cc"
    auth_code = "uB?Zw6ZbW3"

    subject = "BCC text"
    html_content = """
        <h2>您好，</h2>
        <p>这是一个使用 Python 发送的测试邮件，BCC 群发 50 人。</p>
        <p>发送成功请忽略。</p>
        <br><p style="color: gray;">-- Python 邮件机器人</p>
    """

    result = send_email(
        receiver_email=to_email,
        subject=subject,
        html_text=html_content,
        sender_email=sender,
        password=auth_code,
        smtp_host="101.89.86.84",   
        smtp_port=465,
        bcc_list=bcc_emails
    )

    print(result)
