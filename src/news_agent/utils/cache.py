import json
import os

CACHE_FILE = "cache.json"

def load_cache() -> dict:
    """从本地 JSON 文件加载缓存。"""
    if not os.path.exists(CACHE_FILE):
        return {"summary": {}, "category": {}, "category_summary": {}}
    
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 确保所有必要的键都存在
            for key in ["summary", "category", "category_summary"]:
                if key not in data:
                    data[key] = {}
            return data
    except (json.JSONDecodeError, Exception):
        # 如果文件损坏，返回空结构
        return {"summary": {}, "category": {}, "category_summary": {}}

def save_cache(cache_data: dict):
    """将缓存数据保存到本地 JSON 文件。"""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"警告: 保存缓存失败: {e}")

# 全局缓存单例
cache = load_cache()

def get_summary_cache(title: str):
    return cache["summary"].get(title)

def set_summary_cache(title: str, summary: str):
    cache["summary"][title] = summary
    save_cache(cache)

def get_category_cache(title: str):
    return cache["category"].get(title)

def set_category_cache(title: str, category: str):
    cache["category"][title] = category
    save_cache(cache)

def get_category_summary_cache(category: str):
    return cache["category_summary"].get(category)

def set_category_summary_cache(category: str, summary: str):
    cache["category_summary"][category] = summary
    save_cache(cache)

# 分类汇总
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