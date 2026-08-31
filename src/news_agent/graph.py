from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from news_agent.state import AgentState
from news_agent.nodes.fetch_async import fetch_sources_async_node
from news_agent.nodes.dedup import dedup_node
from news_agent.utils.cleaner import clean_articles_node
from news_agent.nodes.classify import classify_node
from news_agent.nodes.summarize import (
    extra_check_node,
    summarize_single_batch_node,
    summarize_category_node,
)
from news_agent.nodes.report import report_node
from news_agent.nodes.send import send_email_node

memory = MemorySaver()
workflow = StateGraph(AgentState)

workflow.add_node("fetch", fetch_sources_async_node)
workflow.add_node("dedup", dedup_node)
workflow.add_node("clean", clean_articles_node)
workflow.add_node("classify", classify_node)
workflow.add_node("extra_check", extra_check_node)
workflow.add_node("single_summarize", summarize_single_batch_node)
workflow.add_node("category_summarize", summarize_category_node)
workflow.add_node("report", report_node)
workflow.add_node("send_email", send_email_node)


def route_after_classify(state: AgentState) -> str:
    articles = state.get("classified_articles", [])
    if len(articles) > 20:
        return "extra_check"
    return "single_summarize"


workflow.set_entry_point("fetch")
workflow.add_edge("fetch", "dedup")
workflow.add_edge("dedup", "clean")
workflow.add_edge("clean", "classify")

workflow.add_conditional_edges(
    "classify",
    route_after_classify,
    {"extra_check": "extra_check", "single_summarize": "single_summarize"},
)

workflow.add_edge("extra_check", "single_summarize")
workflow.add_edge("single_summarize", "category_summarize")
workflow.add_edge("category_summarize", "report")
workflow.add_edge("report", "send_email")
workflow.add_edge("send_email", END)

graph = workflow.compile(checkpointer=memory)
