from __future__ import annotations


INTENT_DAILY_BRIEFING = "daily_briefing"
INTENT_TOPIC_SEARCH = "topic_search"

DAILY_STRONG_KEYWORDS = ("简报", "日报", "早报", "今天", "今日")
DAILY_KEYWORDS = ("最新新闻", "新闻")
TOPIC_KEYWORDS = ("关于", "主题", "搜索", "查找", "查一下", "查一查", "分析")


def detect_intent(query: str) -> str:
    text = (query or "").strip().lower()
    if not text:
        return INTENT_DAILY_BRIEFING

    has_daily_strong_keyword = any(
        keyword.lower() in text for keyword in DAILY_STRONG_KEYWORDS
    )
    has_daily_keyword = has_daily_strong_keyword or any(
        keyword.lower() in text for keyword in DAILY_KEYWORDS
    )
    has_topic_keyword = any(keyword.lower() in text for keyword in TOPIC_KEYWORDS)

    if has_topic_keyword and not has_daily_strong_keyword:
        return INTENT_TOPIC_SEARCH
    if has_daily_keyword:
        return INTENT_DAILY_BRIEFING
    if has_topic_keyword:
        return INTENT_TOPIC_SEARCH
    return INTENT_DAILY_BRIEFING


def extract_topic(query: str) -> str:
    text = (query or "").strip()
    for marker in ("关于", "查一下", "查一查", "搜索", "查找", "主题"):
        if marker in text:
            return text.split(marker, 1)[-1].strip(" ：:，,。.!！?？") or text
    return text
