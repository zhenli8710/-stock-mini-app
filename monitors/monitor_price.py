import os, json, urllib.request, datetime, sys
sys.stdout.reconfigure(encoding="utf-8")

BN = "https://stock-mini-app-production.up.railway.app"
SC_KEY = os.environ.get("SERVERCHAN_KEY", "")
CACHE = os.path.join(os.path.dirname(__file__), "cache", "price_cache.json")

PRODUCTS = [
    {"name": "iPhone 16 Pro", "query": "iPhone 16 Pro 价格 最新"},
    {"name": "MacBook Pro M4", "query": "MacBook Pro M4 价格 最新"},
    {"name": "RTX 5090", "query": "RTX 5090 显卡 价格 最新"},
]

def sc(q, li=3):
    try:
        r = urllib.request.Request(BN + "/api/search", data=json.dumps({"query": q, "limit": li}).encode(), headers={"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(r, timeout=60).read()).get("data", {}).get("web", []) or []
    except: return []

def run():
    old = {}
    if os.path.exists(CACHE):
        try: old = json.load(open(CACHE, "r", encoding="utf-8"))
        except: pass
    new_data = {}
    changes = []
    for prod in PRODUCTS:
        name = prod["name"]
        items = sc(prod["query"], 3)
        titles = [n.get("title","").strip() for n in items if n.get("title")]
        new_data[name] = titles
        old_t = old.get(name, [])
        if old_t and titles != old_t:
            changes.append(f"【{name}】有变动")
            for t in titles[:2]: changes.append(f"  {t}")
        elif not old_t:
            changes.append(f"【{name}】首次监控")
            for t in titles[:2]: changes.append(f"  {t}")
    json.dump(new_data, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if changes and SC_KEY:
        msg = "\n".join(changes)
        d = json.dumps({"title": "价格监控 " + str(datetime.date.today()), "desp": msg}).encode()
        urllib.request.urlopen(urllib.request.Request(f"https://sctapi.ftqq.com/{SC_KEY}.send", data=d, headers={"Content-Type": "application/json"}), timeout=15)
        print("Sent:", len(changes))
    elif changes: print("\n".join(changes))
    else: print("No changes")
if __name__ == "__main__": run()
