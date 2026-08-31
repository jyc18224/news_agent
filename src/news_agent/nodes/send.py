import smtplib
import sys
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from ..utils.logger import logger


def ask_send_confirmation() -> bool:
    """Human-in-the-loop gate before a real email is sent."""
    answer = input("是否发送？Y/N: ").strip().lower()
    return answer in {"y", "yes", "是"}


def send_email(report_md: str, email_config: dict) -> bool:
    """
    通过 SMTP 发送生成的 Markdown 报告邮件。
    """
    if not email_config.get("enabled", False):
        logger.info("邮件通知功能已禁用，跳过发送步骤。")
        return True

    try:
        smtp_server = email_config["smtp_server"]
        smtp_port = email_config["smtp_port"]
        sender_email = email_config["sender"]
        sender_auth_code = email_config["auth_code"]
        to_email = email_config["to"]

        msg = MIMEText(report_md, "plain", "utf-8")
        msg["From"] = Header(f"AI 新闻助手 <{sender_email}>", "utf-8")
        msg["To"] = Header(to_email, "utf-8")
        msg["Subject"] = Header("📰 AI 每日新闻简报", "utf-8")

        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=20) as server:
            server.login(sender_email, sender_auth_code)
            server.sendmail(sender_email, [to_email], msg.as_string())

        logger.info(f"邮件已成功发送至：{to_email}")
        return True
    except KeyError as e:
        logger.error(f"邮件配置项缺失: {e}")
        return False
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        return False


def send_email_node(state: dict) -> dict:
    """
    LangGraph 节点：发送新闻简报邮件。
    """
    logger.info("准备发送邮件通知...")
    start_time = datetime.now()

    email_config = state.get("config", {}).get("email", {})
    report_content = state.get("report", "")

    if email_config.get("confirm_before_send", False):
        if not sys.stdin.isatty():
            logger.warning("非交互环境无法执行人工确认，跳过邮件发送。")
            state["email_sent"] = False
            state["email_error"] = "非交互环境未确认发送"
            return state
        if not ask_send_confirmation():
            logger.info("用户取消了邮件发送。")
            state["email_sent"] = False
            state["email_error"] = "用户取消发送"
            return state

    success = send_email(report_content, email_config)

    cost = (datetime.now() - start_time).total_seconds()
    logger.info(f"邮件任务处理完成 | 耗时: {cost:.2f}s")

    state["email_sent"] = success
    if not success:
        state["email_error"] = "邮件投递失败，请检查系统日志。"

    return state
