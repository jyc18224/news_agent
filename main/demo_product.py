from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEMO_DATE = "2026-08-31"

DEMO_ARTICLES = [
    {
        "category": "科技",
        "title": "OpenAI 发布企业级 Agent 编排平台",
        "summary": "面向企业客户提供可视化多智能体工作流编排、权限控制和日志审计能力。",
        "source": "OpenAI Blog",
        "link": "https://example.com/enterprise-agent-platform",
    },
    {
        "category": "科技",
        "title": "国产大模型密集更新，长文本与推理成本成为竞争焦点",
        "summary": "模型厂商从单纯比拼参数转向比拼可控成本、稳定性和工程落地效率。",
        "source": "TechCrunch AI",
        "link": "https://example.com/chinese-llm-updates",
    },
    {
        "category": "科技",
        "title": "LangGraph 生态持续完善，复杂状态流更适合生产级 Agent",
        "summary": "有向图、持久化 checkpoint 和条件路由让多步骤 Agent 更可控、可观测。",
        "source": "Hacker News",
        "link": "https://example.com/langgraph-production",
    },
    {
        "category": "科技",
        "title": "浏览器 Agent 开始进入日常办公场景",
        "summary": "AI 自动完成表单填写、资料整理和跨平台信息汇总，但稳定性和权限边界仍是挑战。",
        "source": "TechCrunch AI",
        "link": "https://example.com/browser-agent-work",
    },
    {
        "category": "财经",
        "title": "AI 编程赛道融资继续升温，企业软件预算向开发者工具倾斜",
        "summary": "投资机构更关注能直接提升研发效率、可衡量 ROI 的 AI 开发工具。",
        "source": "Hacker News",
        "link": "https://example.com/ai-coding-funding",
    },
    {
        "category": "财经",
        "title": "云厂商加大推理算力投入，模型调用价格持续下降",
        "summary": "推理成本下降会加速 Agent 从演示走向真实业务自动化。",
        "source": "TechCrunch AI",
        "link": "https://example.com/inference-cost-drop",
    },
    {
        "category": "教育",
        "title": "多所高校开设 AI Agent 工程课程，强调项目实践能力",
        "summary": "课程重点从单点 API 调用转向完整流程设计、成本控制和产品化落地。",
        "source": "OpenAI Blog",
        "link": "https://example.com/agent-course",
    },
    {
        "category": "其他",
        "title": "AI 安全监管进入新阶段，生成内容标识成为平台合规重点",
        "summary": "内容来源声明、模型可解释性和审计日志正在成为企业级 AI 产品的基础能力。",
        "source": "Hacker News",
        "link": "https://example.com/ai-compliance",
    },
    {
        "category": "其他",
        "title": "芯片供应链调整，推理芯片需求增速超过训练芯片",
        "summary": "推理负载增加推动芯片厂商优化单位成本、能效和部署密度。",
        "source": "TechCrunch AI",
        "link": "https://example.com/inference-chips",
    },
    {
        "category": "其他",
        "title": "AI 音乐创作工具快速迭代，创作者版权问题再受关注",
        "summary": "工具能力提升很快，但版权归属和收益分配仍需要更明确的行业规则。",
        "source": "Hacker News",
        "link": "https://example.com/ai-music-copyright",
    },
]

DEMO_CATEGORY_SUMMARY = {
    "科技": "科技板块围绕企业级 Agent、大模型推理成本和开发者工具展开，说明 AI 产品正在从单点能力走向可编排、可审计的完整流程。",
    "财经": "财经板块显示资本市场更关注能直接提升研发效率并降低模型调用成本的 AI 基础设施。",
    "教育": "教育板块显示 AI Agent 工程正在进入课程体系，企业需要既懂模型能力又懂工程落地的复合型人才。",
    "其他": "安全合规、算力供应链和内容创作等议题共同指向同一个趋势：AI 产品要从演示走向生产，必须同时考虑成本、可靠性和责任边界。",
}


def render_demo_report(
    articles=None,
    category_summary=None,
    report_date: str = DEMO_DATE,
) -> str:
    articles = articles or DEMO_ARTICLES
    category_summary = category_summary or DEMO_CATEGORY_SUMMARY

    grouped = defaultdict(list)
    for article in articles:
        grouped[article.get("category", "其他")].append(article)

    lines = [
        f"# AI 新闻早报 · 产品示例 {report_date}",
        "",
        "> 本报告由 NewsAgent 自动生成，内容为产品示例。",
        "",
        f"**报告日期：** {report_date}",
        f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**今日抓取总量：** {len(articles)} 篇",
        "",
    ]

    for category in category_summary:
        items = grouped.get(category, [])
        if not items:
            continue
        lines.append(f"## 【{category}】 ({len(items)} 篇)")
        lines.append("")
        lines.append(f"类别综述：{category_summary[category]}")
        lines.append("")
        lines.append("| 标题 | 摘要 | 来源 |")
        lines.append("| :--- | :--- | :--- |")
        for article in items:
            title = article.get("title", "无标题").replace("|", " ").replace("\n", " ")
            summary = (
                article.get("summary", "无摘要").replace("|", " ").replace("\n", " ")
            )
            source = article.get("source", "-").replace("|", " ").replace("\n", " ")
            lines.append(f"| {title} | {summary} | {source} |")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## 今日编辑推荐",
            "",
            "推荐：【OpenAI 发布企业级 Agent 编排平台】",
            "理由：它最完整地体现了本项目的产品价值：把模型能力、工作流编排、成本控制和可观测性组合成一个可交付的自动化产品。",
            "",
            "---",
            "",
            "## 报告说明",
            "",
            "- 数据源：OpenAI Blog、Hacker News、TechCrunch AI",
            "- 今日抓取总量：10 篇",
            "- 分类数：4 类",
            "- 报告状态：已生成",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="生成无需 API 的新闻 Agent 产品演示日报"
    )
    parser.add_argument(
        "--output",
        default="examples/demo_report.md",
        help="输出 Markdown 文件路径（默认：examples/demo_report.md）",
    )
    args = parser.parse_args()

    output_path = PROJECT_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_demo_report(), encoding="utf-8")

    print("演示日报已生成：")
    print(output_path)
    print()


if __name__ == "__main__":
    main()
