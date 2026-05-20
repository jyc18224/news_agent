import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from openai import OpenAI
from ..utils.logger import logger

# LLM 客户端配置
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def pick_editor_recommend(articles: list) -> str:
    """
    使用 LLM 选出最有价值的新闻并给出推荐理由。
    """
    if not articles:
        return "暂无推荐内容。"

    news_text = ""
    for idx, art in enumerate(articles):
        news_text += f"{idx+1}. 标题：{art.get('title', '')}\n摘要：{art.get('summary', '')}\n\n"

    prompt = f"""你是资深的新闻编辑。请从以下新闻列表中选出一条最有价值的新闻，并给出简洁的推荐理由（30-60字）。
格式要求：
推荐：【新闻标题】
理由：...

新闻列表：
{news_text}
"""
    try:
        resp = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"生成编辑推荐失败: {e}")
        return "无法生成推荐。"

def generate_markdown_report(state: dict) -> str:
    """
    生成包含分类表格和编辑推荐的 Markdown 报告。
    """
    articles = state.get("classified_articles", [])
    category_summary = state.get("category_summary", {})
    today = datetime.now().strftime("%Y-%m-%d")

    grouped = defaultdict(list)
    for art in articles:
        cat = art.get("category", "其他")
        grouped[cat].append(art)

    md = f"# AI 新闻简报 {today}\n\n"
    md += f"📊 今日抓取总量：{len(articles)} 篇\n\n"

    for cat, items in grouped.items():
        md += f"## 【{cat}】 ({len(items)} 篇)\n\n"
        
        summary = category_summary.get(cat, {}).get("summary", "暂无汇总摘要。")
        md += f"📝 类别综述：{summary}\n\n"

        md += "| 标题 | 摘要 |\n"
        md += "| :--- | :--- |\n"
        for art in items:
            title = art.get("title", "无标题").replace("|", " ").replace("\n", " ")
            summary = art.get("summary", "无摘要").replace("|", " ").replace("\n", " ")
            md += f"| {title} | {summary} |\n"
        md += "\n"

    md += "---\n\n# 🎯 编辑推荐\n\n"
    md += pick_editor_recommend(articles) + "\n"

    # 将报告持久化存储到本地
    Path("report").mkdir(exist_ok=True)
    filename = f"report/news_daily_{today}.md"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(md)
        logger.info(f"Markdown 报告已生成：{filename}")
    except Exception as e:
        logger.error(f"保存报告文件失败: {e}")

    return md

def report_node(state: dict) -> dict:
    """
    LangGraph 节点：生成最终的新闻报告。
    """
    logger.info("正在生成最终报告...")
    start_time = datetime.now()
    
    report_content = generate_markdown_report(state)
    
    cost = (datetime.now() - start_time).total_seconds()
    logger.info(f"报告生成完成 | 耗时: {cost:.2f}s")
    
    return {"report": report_content}