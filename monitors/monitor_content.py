import os, json, urllib.request, datetime, sys, hashlib
sys.stdout.reconfigure(encoding="utf-8")
BN = "https://stock-mini-app-production.up.railway.app"
SC_KEY = os.environ.get("SERVERCHAN_KEY", "")
CACHE = os.path.join(os.path.dirname(__file__), "cache", "content_cache.json")
URLS = ["https://aichagpt.com/", "https://news.ycombinator.com", "https://36kr.com/information/"]
def scrape(url):
    try:
        r = urllib.request.Request(BN + "/api/scrape", data=json.dumps({"url": url}).encode(), headers={"Content-Type": "application/json"})
        d = json.loads(urllib.request.urlopen(r, timeout=30).read())
        md = d.get("data", {}).get("markdown", "") or d.get("markdown", "")
        return md[:2000] if md else ""
    except: return ""
def run():
    old = {}
    if os.path.exists(CACHE):
        try: old = json.load(open(CACHE, "r", encoding="utf-8"))
        except: pass
    new_data = {}; changes = []
    for url in URLS:
        content = scrape(url)
        h = hashlib.md5(content.encode()).hexdigest()[:8]
        new_data[url] = {"hash": h, "preview": content[:100]}
        old_h = old.get(url, {}).get("hash", "")
        if old_h and h != old_h:
            changes.append(f"【{url}】内容已更新  {content[:80]}")
        elif not old_h:
            changes.append(f"【{url}】首次监控")
    json.dump(new_data, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if changes and SC_KEY:
        msg = "\n".join(changes)
        d = json.dumps({"title": "网站监控 " + str(datetime.date.today()), "desp": msg}).encode()
        urllib.request.urlopen(urllib.request.Request(f"https://sctapi.ftqq.com/{SC_KEY}.send", data=d, headers={"Content-Type": "application/json"}), timeout=15)
        print("Sent:", len(changes))
    elif changes: print("\n".join(changes))
    else: print("No changes")
if __name__ == "__main__": run()
