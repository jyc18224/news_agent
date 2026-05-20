from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from news_agent.state import AgentState
from news_agent.nodes.fetch_async import fetch_sources_async_node
from news_agent.nodes.dedup import dedup_node
from news_agent.utils.cleaner import clean_articles_node
from news_agent.nodes.classify import classify_node
from news_agent.nodes.summarize import extra_check_node, summarize_single_batch_node, summarize_category_node
from news_agent.nodes.report import report_node
from news_agent.nodes.send import send_email_node

# 工作流配置与状态管理
memory = MemorySaver()
workflow = StateGraph(AgentState)

# 注册工作流节点
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
    """
    根据分类后的文章数量进行条件路由。
    如果文章数量超过 20 篇，则进入额外校验节点。
    """
    articles = state.get("classified_articles", [])
    if len(articles) > 20:
        return "extra_check"
    return "single_summarize"

# 定义节点间的连线
workflow.set_entry_point("fetch")
workflow.add_edge("fetch", "dedup")
workflow.add_edge("dedup", "clean")
workflow.add_edge("clean", "classify")

# 条件分支逻辑
workflow.add_conditional_edges(
    "classify",
    route_after_classify,
    {
        "extra_check": "extra_check",
        "single_summarize": "single_summarize"
    }
)

# 分类后的后续处理流程
workflow.add_edge("extra_check", "single_summarize")
workflow.add_edge("single_summarize", "category_summarize")
workflow.add_edge("category_summarize", "report")
workflow.add_edge("report", "send_email")
workflow.add_edge("send_email", END)

# 编译工作流并启用持久化
graph = workflow.compile(checkpointer=memory)