# news_agent/nodes/fetch.py
import feedparser
import requests
# 让 Python 能上网、能下载网页、能调用接口 HTTP 请求库
#如果你直接用 requests 拿到 XML，你还要自己处理格式、提取标题、时间、链接……feedparser 帮你一键解析成字典，超级方便


# 同步抓取单篇RSS
def fetch_from_rss_sync(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.text)

        articles = []
        for entry in feed.entries[:5]:
            articles.append({
                "title": entry.get("title", "无标题"),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", "")
            })
        return articles

    except Exception as e:
        print(f"抓取失败 {url}：{str(e)}")
        return []

# 同步抓取节点（5.17版本）
def fetch_sources_node(state):
    sources = state["config"]["sources"]
    all_articles = []

    print("\n开始同步抓取新闻...")

    for source in sources:
        name = source["name"]
        url = source["url"]
        print(f"\n正在抓取：{name}")

        articles = fetch_from_rss_sync(url)
        all_articles.extend(articles)

        for a in articles:
            print(f"- {a['title']}")
            print(f"  {a['link']}")

    print(f"\n抓取完成！总计文章：{len(all_articles)}")
    return {"raw_articles": all_articles}