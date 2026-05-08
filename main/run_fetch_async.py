# main/run_fetch_async.py
import asyncio
import yaml
from pathlib import Path
import sys

# 这一行是关键！把项目根目录加入路径
sys.path.append(str(Path(__file__).parent.parent))

# 现在可以正常导入模块
from nodes.fetch_async import fetch_sources_async_node

# 加载配置（绝对路径，永远不报错）
def load_config():
    # 定位到项目根目录的 config/sources.yaml
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / "config" / "sources.yaml"

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# 主运行函数
async def main():
    cfg = load_config()
    await fetch_sources_async_node(cfg)

if __name__ == "__main__":
    asyncio.run(main())