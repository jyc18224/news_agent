from news_agent.intent import detect_intent, extract_topic


def test_daily_briefing_intent():
    assert detect_intent("看今日简报") == "daily_briefing"
    assert detect_intent("生成今天的新闻日报") == "daily_briefing"


def test_topic_search_intent():
    assert detect_intent("查一下 AI Agent 主题") == "topic_search"
    assert detect_intent("搜索关于大模型的最新新闻") == "topic_search"


def test_extract_topic():
    assert "大模型" in extract_topic("查一下大模型")
    assert "AI Agent" in extract_topic("关于 AI Agent 的最新进展")
