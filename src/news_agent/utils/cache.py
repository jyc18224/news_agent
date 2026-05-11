import json
import os

CACHE_FILE = "cache.json"

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {
            "summary": {},
            "category": {},
            "category_summary": {}  # 只加这一个
        }
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 自动补全缺失字段，防止 KeyError
            if "summary" not in data:
                data["summary"] = {}
            if "category" not in data:
                data["category"] = {}
            if "category_summary" not in data:
                data["category_summary"] = {}
            return data
    except:
        # 文件损坏直接重建
        return {
            "summary": {},
            "category": {},
            "category_summary": {}
        }
def save_cache(cache_data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

cache = load_cache()

# 单篇摘要
def get_summary_cache(title: str):
    return cache["summary"].get(title)
def set_summary_cache(title: str, summary: str):
    cache["summary"][title] = summary
    save_cache(cache)

# 单篇分类
def get_category_cache(title: str):
    return cache["category"].get(title)
def set_category_cache(title: str, category: str):
    cache["category"][title] = category
    save_cache(cache)

# 分类汇总（只加这个）
def get_category_summary_cache(cat: str):
    return cache["category_summary"].get(cat)
def set_category_summary_cache(cat: str, content: str):
    cache["category_summary"][cat] = content
    save_cache(cache)

# 清空
def clear_all_cache():
    global cache
    cache = {"summary": {}, "category": {}, "category_summary": {}}
    save_cache(cache)