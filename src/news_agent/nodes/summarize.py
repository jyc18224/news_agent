from typing import List, Dict
from collections import defaultdict
from openai import OpenAI
from utils.logger import logger
import os
from datetime import datetime
from utils.cache import (
    get_summary_cache,
    get_category_summary_cache,
    set_category_summary_cache,
    set_summary_cache
)

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# ----------------------
# 5.28 + 5.29 单篇文章摘要（健壮版）
# ----------------------
def generate_summary(article: Dict) -> Dict:
    title = article.get("title", "").strip()
    content = article.get("content", "").strip()

    # ===================== 【缓存：第一步】 =====================
    # 查缓存：如果标题已经处理过，直接返回，不调LLM
    cached = get_summary_cache(title)
    if cached is not None:
        article["summary"] = cached
        return article
    # ==========================================================

    # 文章太短，直接用标题
    if not content or len(content) < 20:
        article["summary"] = title
        # 存进缓存
        set_summary_cache(title, title)
        return article

    prompt = f"""请为新闻生成简洁摘要（20-50字）。
标题：{title}
正文：{content}
摘要："""

    try:
        resp = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100
        )
        summary = resp.choices[0].message.content.strip()
        article["summary"] = summary

        # ===================== 【缓存：第二步】 =====================
        # 生成成功 → 存进缓存
        set_summary_cache(title, summary)
    except Exception as e:
        logger.error(f"摘要失败：{e}")
        # ===================== 【6.5新增】异常兜底 =====================
        article["summary"] = title
        set_summary_cache(title, title)
    return article

# ----------------------
# 5.28 批量单篇摘要节点
# ----------------------
def summarize_single_batch_node(state):
    # 【新增日志】：开始单篇摘要的提示
    logger.info("✍️  开始生成单篇摘要...")
    # 【新增耗时统计】：记录开始时间
    start = datetime.now()
    articles = state.get("classified_articles", [])
    summarized = [generate_summary(art) for art in articles]

    # 【新增耗时统计】：计算并打印耗时
    cost = (datetime.now() - start).total_seconds()
    logger.info(f"✅ 单篇摘要完成：{len(summarized)} 篇 | 耗时 {cost:.2f}s")
    return {"classified_articles": summarized}

# ----------------------
# 5.27 类别汇总摘要
# ----------------------
def summarize_by_category(articles: List[Dict]) -> Dict:
    from collections import defaultdict
    grouped = defaultdict(list)
    for art in articles:
        cat = art.get("category", "其他")
        grouped[cat].append(art)

    category_summary = {}
    for cat, arts in grouped.items():
        # ========== 缓存：同类目只汇总一次，不重复调用 LLM ==========
        cached_summary = get_category_summary_cache(cat)
        if cached_summary is not None:
            category_summary[cat] = {
                "count": len(arts),
                "summary": cached_summary
            }
            continue
        texts = [f"【新闻{i + 1}】{a.get('title', '无标题')}\n{a.get('content', '')}" for i, a in enumerate(arts)]
        all_text = "\n".join(texts)

        prompt = f"""你是专业新闻编辑，请对【{cat}】类新闻生成一段80-150字汇总摘要。
新闻内容：
{all_text}

汇总摘要："""

        try:
            resp = client.chat.completions.create(
                model="qwen-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            summary = resp.choices[0].message.content.strip()
            category_summary[cat] = {"count": len(arts), "summary": summary}
        except:
            category_summary[cat] = {"count": len(arts), "summary": "汇总失败"}
    return category_summary

# ----------------------
# 5.27 汇总摘要节点
# ----------------------
def summarize_category_node(state):
    # 【新增日志】：开始分类汇总的提示
    logger.info("📝 开始生成分类汇总...")
    # 【新增耗时统计】：记录开始时间
    start = datetime.now()

    articles = state.get("classified_articles", [])
    summary_result = summarize_by_category(articles)

    # 【新增耗时统计】：计算并打印耗时
    cost = (datetime.now() - start).total_seconds()
    logger.info(f"✅ 分类汇总完成，共 {len(summary_result)} 类 | 耗时 {cost:.2f}s")
    return {
        "classified_articles": articles,
        "category_summary": summary_result
    }

# ----------------------
# 5.28 额外检查节点
# ----------------------
def extra_check_node(state):
    count = len(state.get("classified_articles", []))
    logger.info(f"⚠️ 进入额外检查：文章数量 {count}（>20）")
    logger.info("✅ 额外检查完成")
    return state