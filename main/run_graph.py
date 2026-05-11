import asyncio
import sys
from datetime import datetime
from pathlib import Path

import yaml
from news_agent.graph import graph  # 这里改成包导入
from news_agent.utils.logger import logger
PROJECT_ROOT = Path(__file__).parent.parent


def load_config(sources_path="config/sources.yaml"):
    # 支持传入自定义路径
    config_path = PROJECT_ROOT / sources_path
    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path}")
        return {"sources": []}

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ====================== 6.10 封装成函数 ======================
async def run_news_agent(sources_path="config/sources.yaml", output_path="report.md"):
    total_start = datetime.now()
    logger.info("======================================")
    logger.info("       新闻AI工作流 开始运行           ")
    logger.info("======================================")

    config = load_config(sources_path)

    initial_state = {
        "config": config,
        "raw_articles": [],
        "deduped_articles": [],
        "cleaned_articles": [],
        "classified_articles": [],
        "category_summary": {},
        "report": ""
    }

    run_config = {
        "configurable": {"thread_id": "news_agent"}
    }

    try:
        final_state = await graph.ainvoke(initial_state, run_config)

        total_cost = (datetime.now() - total_start).total_seconds()
        logger.info("======================================")
        logger.info(f"🏁 全部流程完成！总耗时：{total_cost:.2f}s")
        logger.info("======================================")

        print("\n" + "=" * 50)
        print("✅ 流程全部运行完成！")

        print(f"原始文章: {len(final_state.get('raw_articles', []))} 篇")
        print(f"清洗后: {len(final_state.get('cleaned_articles', []))} 篇")
        print(f"分类后: {len(final_state.get('classified_articles', []))} 篇")

        category_summary = final_state.get('category_summary', {})
        print(f"生成的分类汇总: {len(category_summary)} 类")

        if category_summary:
            print("\n📝 分类汇总简报：")
            for cat, data in category_summary.items():
                count = data.get('count', 0) if isinstance(data, dict) else 0
                summary = data.get('summary', '无摘要') if isinstance(data, dict) else str(data)
                print(f"\n【{cat}】（共{count}篇）")
                print(summary)
        else:
            print("\n⚠️ 未生成分类汇总，请检查日志。")

        print("=" * 50)

        # ====================== 自动保存报告 ======================
        report_content = final_state.get("report", "")
        if report_content:
            output_full_path = PROJECT_ROOT / output_path
            with open(output_full_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            logger.info(f"报告已保存到：{output_full_path}")

    except Exception as e:
        logger.error(f"❌ 流程运行出错: {str(e)}", exc_info=True)
        print(f"\n❌ 发生错误: {str(e)}")
        print("请查看日志文件获取详细错误信息。")


# ====================== 主入口 ======================
async def main():
    await run_news_agent()


if __name__ == "__main__":
    asyncio.run(main())