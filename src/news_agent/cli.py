#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
6.10 命令行工具：新闻摘要 Agent CLI
支持：--sources 指定配置文件
      --output 指定输出报告
"""
import argparse
import sys
from pathlib import Path

# --- 新增：确保根目录在路径中 ---
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# --- 新增结束 ---

from main.run_graph import run_news_agent  # 导入你的主程序入口


def main():
    # 1. 创建命令行解析器
    parser = argparse.ArgumentParser(
        description="AI 自动新闻摘要 Agent - 命令行工具"
    )

    # 2. 添加命令行参数
    parser.add_argument(
        "--sources",
        type=str,
        default="config/sources.yaml",
        help="指定数据源配置文件路径（默认：config/sources.yaml）"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="report.md",
        help="指定输出报告文件路径（默认：report.md）"
    )

    # 3. 解析用户输入的参数
    args = parser.parse_args()

    # 4. 打印信息，方便查看
    print("=" * 50)
    print(f"📥 使用配置文件：{args.sources}")
    print(f"📤 报告将输出到：{args.output}")
    print("=" * 50)
    print()

    # 5. 运行你的新闻 Agent
    try:
        # 注意：run_news_agent 是 async 函数，这里需要 asyncio.run
        import asyncio
        asyncio.run(run_news_agent(
            sources_path=args.sources,
            output_path=args.output
        ))
        print(f"\n✅ 运行完成！报告已保存到：{args.output}")
    except Exception as e:
        print(f"\n❌ 运行出错：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()