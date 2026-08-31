import argparse
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from news_agent.config import PROJECT_ROOT, load_config
from news_agent.graph import graph
from news_agent.utils.logger import logger

# 加载环境变量
load_dotenv()


async def run_news_agent(
    sources_path="config/sources.yaml",
    output_path="report.md",
    confirm_email=False,
    send_email=None,
):
    """运行新闻 Agent 工作流的主函数。"""
    total_start = datetime.now()
    logger.info("=" * 40)
    logger.info("       新闻 AI Agent 开始运行           ")
    logger.info("=" * 40)

    config = load_config(sources_path)
    email_config = config.setdefault("email", {})
    if send_email is False:
        email_config["enabled"] = False
    if send_email is True:
        email_config["enabled"] = True
    if confirm_email:
        email_config["confirm_before_send"] = True

    initial_state = {
        "config": config,
        "raw_articles": [],
        "deduped_articles": [],
        "cleaned_articles": [],
        "classified_articles": [],
        "category_summary": {},
        "report": "",
        "email_sent": False,
        "email_error": None,
    }

    # 线程 ID 用于持久化存储区分不同的会话
    run_config = {"configurable": {"thread_id": "news_agent"}}

    try:
        final_state = await graph.ainvoke(initial_state, run_config)

        total_cost = (datetime.now() - total_start).total_seconds()
        logger.info("=" * 40)
        logger.info(f"工作流运行完成！总耗时: {total_cost:.2f}s")
        logger.info("=" * 40)

        # 打印执行统计信息
        print(f"\n{'='*20} 运行统计 {'='*20}")
        print(f"原始文章数: {len(final_state.get('raw_articles', []))}")
        print(f"清洗后数量: {len(final_state.get('cleaned_articles', []))}")
        print(f"分类后数量: {len(final_state.get('classified_articles', []))}")

        category_summary = final_state.get("category_summary", {})
        if category_summary:
            print("\n各类别文章统计:")
            for cat, data in category_summary.items():
                count = data.get("count", 0) if isinstance(data, dict) else 0
                print(f"- 【{cat}】 ({count} 篇)")

        # 检查邮件发送状态
        email_sent = final_state.get("email_sent", False)
        email_error = final_state.get("email_error")
        if email_sent:
            logger.info("邮件发送成功！")
        elif email_error:
            logger.error(f"邮件发送失败: {email_error}")

        # 将生成的 Markdown 报告保存到文件
        report_content = final_state.get("report", "")
        if report_content:
            output_full_path = PROJECT_ROOT / output_path
            with open(output_full_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            logger.info(f"报告已保存至: {output_full_path}")

    except Exception as e:
        logger.error(f"工作流执行过程中发生错误: {str(e)}", exc_info=True)
        raise


async def main():
    parser = argparse.ArgumentParser(description="AI 自动新闻摘要 Agent")
    parser.add_argument("--sources", default="config/sources.yaml")
    parser.add_argument("--output", default="report.md")
    parser.add_argument(
        "--confirm-email", action="store_true", help="发送邮件前要求 Y/N 确认"
    )
    parser.add_argument("--no-send", action="store_true", help="禁止发送邮件")
    args = parser.parse_args()

    await run_news_agent(
        sources_path=args.sources,
        output_path=args.output,
        confirm_email=args.confirm_email,
        send_email=False if args.no_send else None,
    )


if __name__ == "__main__":
    asyncio.run(main())
