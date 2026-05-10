import asyncio
import sys
from datetime import datetime
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from graph import graph
from utils.logger import logger


def load_config():
    # 使用 resolve() 确保路径正确
    config_path = PROJECT_ROOT / "config" / "sources.yaml"
    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path}")
        # 返回一个空的默认配置，防止程序直接崩溃，或者你可以选择退出
        return {"sources": []}

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def main():
    total_start = datetime.now()
    logger.info("======================================")
    logger.info("       新闻AI工作流 开始运行           ")
    logger.info("======================================")

    config = load_config()

    # 初始化状态
    # 注意：确保 state.py 中 AgentState 的字段都有默认值，或者在这里显式初始化
    initial_state = {
        "config": config,
        "raw_articles": [],
        "deduped_articles": [],  # 确认你的 state 里是否有这个字段，如果没有会报错
        "cleaned_articles": [],
        "classified_articles": [],
        "category_summary": {},
        "report": ""
    }

    run_config = {
        "configurable": {"thread_id": "news_agent"}
    }

    try:
        # 执行图
        # 建议：如果你的 Graph 入口定义了 Input 类型，这里应该传 Input 对象
        # 如果是直接传 State，则传 initial_state
        final_state = await graph.ainvoke(initial_state, run_config)

        # 成功后的统计
        total_cost = (datetime.now() - total_start).total_seconds()
        logger.info("======================================")
        logger.info(f"🏁 全部流程完成！总耗时：{total_cost:.2f}s")
        logger.info("======================================")

        # 安全地打印结果
        print("\n" + "=" * 50)
        print("✅ 流程全部运行完成！")

        # 使用 .get() 防止 KeyError
        print(f"原始文章: {len(final_state.get('raw_articles', []))} 篇")
        print(f"清洗后: {len(final_state.get('cleaned_articles', []))} 篇")
        print(f"分类后: {len(final_state.get('classified_articles', []))} 篇")

        category_summary = final_state.get('category_summary', {})
        print(f"生成的分类汇总: {len(category_summary)} 类")

        if category_summary:
            print("\n📝 分类汇总简报：")
            for cat, data in category_summary.items():
                # 防御性编程：防止 data 格式不对
                count = data.get('count', 0) if isinstance(data, dict) else 0
                summary = data.get('summary', '无摘要') if isinstance(data, dict) else str(data)
                print(f"\n【{cat}】（共{count}篇）")
                print(summary)
        else:
            print("\n⚠️ 未生成分类汇总，请检查日志。")

        print("=" * 50)

    except Exception as e:
        # 捕获所有异常，防止程序崩溃且无日志
        logger.error(f"❌ 流程运行出错: {str(e)}", exc_info=True)
        print(f"\n❌ 发生错误: {str(e)}")
        print("请查看日志文件获取详细错误信息。")


if __name__ == "__main__":
    asyncio.run(main())