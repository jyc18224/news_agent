from typing import TypedDict, List, Dict


class AgentState(TypedDict):
    config: dict
    raw_articles: List[Dict]
    deduped_articles: List[Dict]
    cleaned_articles: List[Dict]
    classified_articles: List[Dict]
    category_summary: Dict[str, Dict]
    report: str
    email_sent: bool
    email_error: str | None
