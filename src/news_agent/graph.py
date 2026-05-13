from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from news_agent.state import AgentState
from news_agent.nodes.fetch_async import fetch_sources_async_node
from news_agent.nodes.dedup import dedup_node
from news_agent.utils.cleaner import clean_articles_node
from news_agent.nodes.classify import classify_node
from news_agent.nodes.summarize import extra_check_node
from news_agent.nodes.summarize import summarize_single_batch_node
from news_agent.nodes.summarize import summarize_category_node
from news_agent.nodes.report import report_node
from news_agent.nodes.send import send_email_node
# 6.3 持久化（必须加）
# ======================
memory = MemorySaver()
workflow = StateGraph(AgentState)

# 注册所有节点
workflow.add_node("fetch", fetch_sources_async_node)
workflow.add_node("dedup", dedup_node)
workflow.add_node("clean", clean_articles_node)
workflow.add_node("classify", classify_node)
workflow.add_node("extra_check", extra_check_node)
workflow.add_node("single_summarize", summarize_single_batch_node)
workflow.add_node("category_summarize", summarize_category_node)
workflow.add_node("report", report_node)
workflow.add_node("send_email", send_email_node)

# 条件路由：分类后 判断文章是否大于20
def route_after_classify(state):
    art_count = len(state.get("classified_articles", []))
    if art_count > 20:
        return "extra_check"
    return "single_summarize"

# 基础串行流程
workflow.set_entry_point("fetch")
workflow.add_edge("fetch", "dedup")
workflow.add_edge("dedup", "clean")
workflow.add_edge("clean", "classify")

# 关键：条件边 5.28 核心要求
workflow.add_conditional_edges(
    "classify",
    route_after_classify,
    {
        "extra_check": "extra_check",
        "single_summarize": "single_summarize"
    }
)

# 后续串联
workflow.add_edge("extra_check", "single_summarize")
workflow.add_edge("single_summarize", "category_summarize")
workflow.add_edge("category_summarize", "report")

workflow.add_edge("report", "send_email")
workflow.add_edge("send_email", END)

# 6.3 开启持久化 + 中断
# ======================
graph = workflow.compile(
    checkpointer=memory
)