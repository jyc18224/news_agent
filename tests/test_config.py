import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "sources.yaml"


def test_config_file_exists():
    assert CONFIG_PATH.exists(), f"❌ 配置文件不存在：{CONFIG_PATH}"


def test_config_loads_correctly():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    assert config is not None, "❌ 配置文件为空或格式错误"
    assert "sources" in config, "❌ 配置文件缺少 'sources' 字段"
    assert isinstance(config["sources"], list), "❌ 'sources' 必须是列表"


def test_sources_have_required_fields():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    for i, source in enumerate(config["sources"]):
        assert "name" in source, f"❌ 第 {i + 1} 个源缺少 'name' 字段"
        assert "url" in source, f"❌ 第 {i + 1} 个源缺少 'url' 字段"
        assert "type" in source, f"❌ 第 {i + 1} 个源缺少 'type' 字段"


def test_global_config_is_valid():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    global_config = config.get("config", {})
    assert isinstance(global_config, dict), "❌ 'config' 必须是字典"

    if global_config:
        assert isinstance(
            global_config.get("max_articles_per_source"), int
        ), "❌ max_articles_per_source 必须是整数"
        assert isinstance(
            global_config.get("timeout_seconds"), int
        ), "❌ timeout_seconds 必须是整数"
