# main/run_fetch.py
import yaml
from pathlib import Path
import sys

# 这一行是关键！把项目根目录加入路径
sys.path.append(str(Path(__file__).parent.parent))

# 现在可以正常导入模块
from nodes.fetch import fetch_sources_node

# 加载配置（绝对路径）
def load_config():
    # 定位到项目根目录的 config/sources.yaml
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / "config" / "sources.yaml"

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

#从每个 RSS 抓取最新 5 篇文章，打印标题和链接。
#主运行函数
def main() :
    cfg = load_config()
    result = fetch_sources_node({"config": cfg})
    print(f"\n✅ 同步抓取完成，共 {len(result['raw_articles'])} 篇文章")


if __name__ == "__main__":
    main()