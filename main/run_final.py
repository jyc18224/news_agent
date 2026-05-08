import asyncio
import yaml
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from state import AgentState
from graph import graph

def load_config():
    base = Path(__file__).parent.parent
    path = base / "config" / "sources.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

async def main():
    config = load_config()
    initial_state: AgentState = {
        "config": config,
        "raw_articles": [],
        "deduped_articles": [],
        "cleaned_articles": []
    }

    final = await graph.ainvoke(initial_state)

    print("\n" + "="*60)
    print("📊 最终结果")
    print(f"原始文章：{len(final['raw_articles'])}")
    print(f"去重后：{len(final['deduped_articles'])}")
    print(f"清洗后：{len(final['cleaned_articles'])}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
