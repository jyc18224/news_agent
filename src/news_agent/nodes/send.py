# nodes/send.py  6.2 配置化版本
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from ..utils.logger import logger
from datetime import datetime

def send_email(report_md: str, email_config: dict):

    if not email_config.get("enabled", False):
        logger.info("📩 邮件功能已关闭，跳过发送")
        return True

    smtp_server = email_config["smtp_server"]
    smtp_port = email_config["smtp_port"]
    sender_email = email_config["sender"]
    sender_auth_code = email_config["auth_code"]
    to_email = email_config["to"]

    msg = MIMEText(report_md, "plain", "utf-8")
    msg["From"] = Header(f"AI新闻日报 <{sender_email}>", "utf-8")
    msg["To"] = Header(to_email, "utf-8")
    msg["Subject"] = Header("📰 AI 新闻日报 | 自动推送", "utf-8")

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=20) as server:
            server.login(sender_email, sender_auth_code)
            server.sendmail(sender_email, [to_email], msg.as_string())
        logger.info(f"✅ 邮件发送成功 → {to_email}")
        return True
    except Exception as e:
        logger.error(f"❌ 邮件发送失败：{str(e)}")
        return False

# 6.2 从 config 读取
def send_email_node(state):
    # 【新增日志】：开始发送邮件的提示
    logger.info("📧 准备发送邮件...")
    # 【新增耗时统计】：记录开始时间
    start = datetime.now()
    # ===================== 【6.5新增】安全获取邮箱配置 =====================
    email_config = state.get("config", {}).get("email", {})
    report_content = state.get("report", "")
    send_email(report_content, email_config)
    # 【新增耗时统计】：计算并打印耗时
    cost = (datetime.now() - start).total_seconds()
    logger.info(f"📧 邮件处理完成 | 耗时 {cost:.2f}s")
    return state