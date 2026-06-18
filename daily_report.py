import urllib.request, json, datetime, os, sys
sys.stdout.reconfigure(encoding="utf-8")

KEY = os.environ.get("SERVERCHAN_KEY", "")
BN = "https://stock-mini-app-production.up.railway.app"
TODAY = datetime.date.today().strftime("%Y.%m.%d")
WDAY = ["一","二","三","四","五","六","日"][datetime.date.today().weekday()]

def sc(q, li=3):
    try:
        r = urllib.request.Request(BN + "/api/search",
            data=json.dumps({"query": q, "limit": li}).encode(),
            headers={"Content-Type": "application/json"})
        d = json.loads(urllib.request.urlopen(r, timeout=60).read())
        return d.get("data", {}).get("web", []) or d.get("web", [])
    except:
        return []

def build():
    lines = [f"StockMini 要闻 | {TODAY} 周{WDAY}", "", "—" * 20, ""]

    queries = [
        "美股 美联储 利率 重大 财经 新闻 突发",
        "A股 收盘 涨跌 政策 利好 利空 最新 消息",
        "港股 恒生 中概 黄金 比特币 原油",
        "人民币 汇率 美元 离岸 升值 贬值 最新",
    ]

    all_items = []
    seen = set()
    for q in queries:
        for n in sc(q, 3):
            t = n.get("title", "").strip()
            u = n.get("url", "")
            desc = (n.get("description", "") or "")[:150]
            if t and u not in seen:
                if any("\u4e00" <= c <= "\u9fff" for c in t):
                    seen.add(u)
                    all_items.append((t, u, desc))

    for i, (t, u, desc) in enumerate(all_items[:8], 1):
        lines.append(f"{i}. [{t}]({u})")
        if desc:
            lines.append(f"   {desc}")
        lines.append("")

    if len(lines) < 6:
        lines.append("（暂无要闻）")
        lines.append("")

    lines.append("—" * 20)
    lines.append(f"Firecrawl | {TODAY}")
    return "\n".join(lines)

if __name__ == "__main__":
    r = build()
    print(r)
    if KEY:
        data = json.dumps({"title": f"StockMini {TODAY}", "desp": r}).encode()
        req = urllib.request.Request(f"https://sctapi.ftqq.com/{KEY}.send",
            data=data, headers={"Content-Type": "application/json"})
        resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
        print("OK" if resp.get("code") == 0 else "Fail")
