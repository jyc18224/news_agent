# 这是整个 Agent 的“数据车厢”
# 所有节点都从这里拿数据、放数据

from typing import TypedDict, List, Dict
from langgraph.graph import END


class AgentState(TypedDict):
    config: dict
    raw_articles: List[Dict]
    deduped_articles: List[Dict]  # 去重后【新增！】
    cleaned_articles: List[Dict]
    classified_articles: List[Dict]
    category_summary: Dict[str, Dict]
    report: str  # 存5.30要的报告文本
