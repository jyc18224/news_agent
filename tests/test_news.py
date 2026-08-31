import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main.demo_product import DEMO_ARTICLES, render_demo_report
from news_agent.nodes.dedup import dedup_node
from news_agent.utils.cleaner import clean_text


def test_clean_text_removes_html_and_whitespace():
    result = clean_text("<p>  hello   world </p>")
    assert result == "hello world"


def test_clean_text_handles_empty_input():
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_dedup_node_removes_duplicate_titles():
    state = {
        "raw_articles": [
            {"title": "重复新闻"},
            {"title": "重复新闻"},
            {"title": "独立新闻"},
        ]
    }
    result = dedup_node(state)
    titles = [article["title"] for article in result["deduped_articles"]]
    assert titles == ["重复新闻", "独立新闻"]


def test_demo_report_contains_product_output():
    report = render_demo_report()
    assert "# AI 新闻早报" in report
    assert "今日抓取总量" in report
    assert "编辑推荐" in report
    assert "演示模式" in report


def test_demo_articles_have_required_fields():
    for article in DEMO_ARTICLES:
        assert article["title"]
        assert article["summary"]
        assert article["category"]
