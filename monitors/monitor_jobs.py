import os, json, urllib.request, datetime, sys
sys.stdout.reconfigure(encoding="utf-8")

BN = "https://stock-mini-app-production.up.railway.app"
SC_KEY = os.environ.get("SERVERCHAN_KEY", "")
CACHE = os.path.join(os.path.dirname(__file__), "cache", "jobs_cache.json")

JOBS = [
    {"name": "Python工程师 北京", "query": "Python工程师 招聘 北京 2026"},
    {"name": "数据分析师 上海", "query": "数据分析师 招聘 上海 2026"},
    {"name": "产品经理 深圳", "query": "产品经理 招聘 深圳 2026"},
    {"name": "AI工程师", "query": "AI人工智能工程师 招聘 最新 2026"},
]

def sc(q, li=5):
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
    for job in JOBS:
        name = job["name"]
        items = sc(job["query"], 5)
        titles = [n.get("title","").strip() for n in items if n.get("title")]
        new_data[name] = titles
        old_t = old.get(name, [])
        if old_t and titles != old_t:
            new_urls = [t for t in titles if t not in old_t]
            if new_urls:
                changes.append(f"【{name}】新增 {len(new_urls)} 个岗位")
                for t in new_urls[:3]: changes.append(f"  {t}")
        elif not old_t:
            changes.append(f"【{name}】首次监控 ({len(titles)} 个)")
            for t in titles[:3]: changes.append(f"  {t}")
    json.dump(new_data, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if changes and SC_KEY:
        msg = "\n".join(changes)
        d = json.dumps({"title": "岗位监控 " + str(datetime.date.today()), "desp": msg}).encode()
        urllib.request.urlopen(urllib.request.Request(f"https://sctapi.ftqq.com/{SC_KEY}.send", data=d, headers={"Content-Type": "application/json"}), timeout=15)
        print("Sent:", len(changes))
    elif changes: print("\n".join(changes))
    else: print("No changes")
if __name__ == "__main__": run()
