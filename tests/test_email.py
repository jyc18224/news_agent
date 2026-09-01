from unittest.mock import patch

from news_agent.nodes.send import send_email, send_email_node


EMAIL_CONFIG = {
    "enabled": True,
    "smtp_server": "smtp.example.com",
    "smtp_port": 465,
    "sender": "sender@example.com",
    "auth_code": "auth-code",
    "to": "to@example.com",
}


@patch("news_agent.nodes.send.smtplib.SMTP_SSL")
def test_send_email_success(mock_smtp):
    context = mock_smtp.return_value.__enter__.return_value

    result = send_email("# 测试日报", EMAIL_CONFIG)

    assert result is True
    context.login.assert_called_once_with("sender@example.com", "auth-code")
    context.sendmail.assert_called_once()


def test_send_email_skips_when_disabled():
    result = send_email("# 测试日报", {"enabled": False})
    assert result is True


def test_send_email_node_marks_disabled_as_not_sent():
    state = {
        "config": {"email": {"enabled": False}},
        "report": "# 测试日报",
        "email_sent": True,
        "email_error": "旧错误",
    }
    result = send_email_node(state)
    assert result["email_sent"] is False
    assert result["email_error"] is None
