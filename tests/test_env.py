import sys
import importlib
import yaml
from pathlib import Path

CONFIG_PATH = Path("../config/sources.yaml")

def test_python_version():
    python_version = sys.version.split()[0]
    assert python_version.startswith("3.11"), "Python 版本必须是 3.11"

def test_required_packages_installed():
    required_packages = [
        "feedparser",
        "aiohttp",
        "langgraph",
        "chromadb",
        "sentence_transformers",
        "yaml"
    ]

    for pkg in required_packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            assert False, f"❌ 包未安装：{pkg}"

def test_config_file_exists():
    assert CONFIG_PATH.exists(), f"配置文件不存在：{CONFIG_PATH}"

def test_config_readable():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    assert "sources" in config

def test_each_source_has_name_url():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    for s in config["sources"]:
        assert "name" in s
        assert "url" in s