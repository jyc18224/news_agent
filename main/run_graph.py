import os
import re
import asyncio
import yaml
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from news_agent.graph import graph
from news_agent.utils.logger import logger

# 加载环境变量
load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent

def load_config(sources_path="config/sources.yaml"):
    """加载并解析配置文件，支持环境变量替换。"""
    config_path = PROJECT_ROOT / sources_path
    if not config_path.exists():
        logger.error(f"未找到配置文件: {config_path}")
        return {"sources": []}

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    def replace_env_var(match):
        var_name = match.group(1)
        var_value = os.getenv(var_name)
        if var_value is None:
            logger.warning(f"未找到环境变量 {var_name}，保持原样")
            return match.group(0)
        return var_value

    # 解析 ${VAR_NAME} 语法并替换为环境变量值
    expanded_content = re.sub(r"\$\{([^}^{]+)\}", replace_env_var, content)

    try:
        return yaml.safe_load(expanded_content)
    except yaml.YAMLError as e:
        logger.error(f"YAML 解析错误: {e}")
        return {}

async def run_news_agent(sources_path="config/sources.yaml", output_path="report.md"):
    """运行新闻 Agent 工作流的主函数。"""
    total_start = datetime.now()
    logger.info("=" * 40)
    logger.info("       新闻 AI Agent 开始运行           ")
    logger.info("=" * 40)

    config = load_config(sources_path)
    initial_state = {
        "config": config,
        "raw_articles": [],
        "deduped_articles": [],
        "cleaned_articles": [],
        "classified_articles": [],
        "category_summary": {},
        "report": "",
        "email_sent": False,
        "email_error": None
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

        category_summary = final_state.get('category_summary', {})
        if category_summary:
            print("\n各类别文章统计:")
            for cat, data in category_summary.items():
                count = data.get('count', 0) if isinstance(data, dict) else 0
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
    await run_news_agent()

if __name__ == "__main__":
    asyncio.run(main())