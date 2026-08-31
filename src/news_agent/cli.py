import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main.run_graph import run_news_agent  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="AI 自动新闻摘要 Agent - 命令行工具"
    )

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

    args = parser.parse_args()

    # 4. 打印信息，方便查看
    print("=" * 50)
    print(f"📥 使用配置文件：{args.sources}")
    print(f"📤 报告将输出到：{args.output}")
    print("=" * 50)
    print()

    try:
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
