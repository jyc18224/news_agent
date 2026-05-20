from typing import TypedDict, List, Dict

class AgentState(TypedDict):
    """
    表示新闻 AI Agent 工作流的状态。
    该架构定义了 LangGraph 中节点之间传递的数据。
    """
    config: dict                     # 基础配置信息
    raw_articles: List[Dict]         # 原始抓取的文章列表
    deduped_articles: List[Dict]     # 去重后的文章列表
    cleaned_articles: List[Dict]     # 清洗后的文章列表
    classified_articles: List[Dict]  # 分类及摘要后的文章列表
    category_summary: Dict[str, Dict] # 各类别汇总摘要
    report: str                      # 最终生成的报告文本
    email_sent: bool                 # 邮件是否发送成功
    email_error: str | None          # 邮件发送失败时的错误信息
