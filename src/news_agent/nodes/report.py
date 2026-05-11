# nodes/report.py  5.30 正式版（Markdown表格 + 存入state）
from ..utils.logger import logger
from datetime import datetime
from pathlib import Path
from collections import defaultdict


# ----------------------
# 5.30 核心：生成带 Markdown 表格的报告
# ----------------------
def generate_markdown_report(state):
    articles = state.get("classified_articles", [])
    category_summary = state.get("category_summary", {})
    today = datetime.now().strftime("%Y-%m-%d")

    # 分组
    grouped = defaultdict(list)
    for art in articles:
        cat = art.get("category", "其他")
        grouped[cat].append(art)

    # 构建 Markdown
    md = f"# AI 新闻日报 {today}\n\n"
    md += f"📊 抓取总数：{len(articles)} 篇\n\n"

    # 每个分类一段
    for cat, items in grouped.items():
        md += f"## 【{cat}】({len(items)}篇)\n\n"

        # 分类汇总摘要
        summary = category_summary.get(cat, {}).get("summary", "无汇总")
        md += f"📝 分类汇总：{summary}\n\n"

        # Markdown 表格（5.30 核心）
        md += "| 标题 | 摘要 |\n"
        md += "|------|------|\n"
        for art in items:
            title = art.get("title", "无标题").replace("|", "").replace("\n", " ")
            summary = art.get("summary", "无摘要").replace("|", "").replace("\n", " ")
            md += f"| {title} | {summary} |\n"
        md += "\n"
    # 5.31 增加编辑推荐板块
    from .report import pick_editor_recommend
    recommend_text = pick_editor_recommend(articles)
    md += "\n---\n\n# 🎯 编辑推荐\n\n"
    md += recommend_text + "\n"

    # 保存文件
    Path("report").mkdir(exist_ok=True)
    filename = f"report/news_daily_{today}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md)

    logger.info(f"✅ Markdown表格报告已生成：{filename}")
    return md

# ----------------------
# 5.30 report_node：存入 state["report"]
# ----------------------
def report_node(state):
    # 【新增日志】：开始生成报告的提示
    logger.info("📄 开始生成Markdown报告...")
    # 【新增耗时统计】：记录开始时间
    start = datetime.now()
    report_content = generate_markdown_report(state)

    # 【新增耗时统计】：计算并打印耗时
    cost = (datetime.now() - start).total_seconds()
    logger.info(f"✅ 报告生成完成 | 耗时 {cost:.2f}s")
    # 关键：把报告写入state
    return {
        "report": report_content
    }

# ----------------------
# 5.31 LLM 选出编辑推荐
# ----------------------
def pick_editor_recommend(articles):
    if not articles:
        return "暂无推荐新闻"

    # 精简所有新闻给LLM
    news_text = ""
    for idx, art in enumerate(articles):
        title = art.get("title", "")
        summary = art.get("summary", "")
        news_text += f"{idx+1}. 标题：{title}\n摘要：{summary}\n\n"

    prompt = f"""你是资深科技编辑，从下面所有新闻中
选出**一条最有价值、最值得关注**的新闻，
写一句简短推荐理由（30-60字）。

只返回格式：
推荐：【新闻标题】
理由：xxx

新闻列表：
{news_text}
"""
    try:
        from openai import OpenAI
        import os
        client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        resp = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=200
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"编辑推荐生成失败：{e}")
        return "编辑推荐：暂无法生成"