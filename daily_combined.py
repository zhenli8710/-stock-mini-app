import os, json, sys, datetime, urllib.request
sys.stdout.reconfigure(encoding="utf-8")
SC_KEY = os.environ.get("SERVERCHAN_KEY", "")
BN = "https://stock-mini-app-production.up.railway.app"
BASE = os.path.dirname(__file__)
TODAY = datetime.date.today()

def sc(q, li=3):
    try:
        r = urllib.request.Request(BN+"/api/search",data=json.dumps({"query":q,"limit":li}).encode(),headers={"Content-Type":"application/json"})
        d = json.loads(urllib.request.urlopen(r,timeout=60).read())
        return d.get("data",{}).get("web",[]) or []
    except: return []

def monitor(items, cf):
    old = {}; changes = []
    if os.path.exists(cf):
        try: old = json.load(open(cf,"r",encoding="utf-8"))
        except: pass
    nd = {}
    for item in items:
        r = sc(item["q"],3)
        t = [n.get("title","").strip() for n in r if n.get("title")]
        nd[item["n"]] = t
        ot = old.get(item["n"],[])
        if ot and t!=ot:
            nu = [x for x in t if x not in ot]
            if nu: changes.append(f"\u25b8 {item['n']}: {len(nu)}条新")
        elif not ot:
            changes.append(f"\u25b8 {item['n']}: 首次({len(t)}条)")
    json.dump(nd,open(cf,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    return changes

lines = [f"StockMini \u7efc\u5408\u65e5\u62a5 | {TODAY}", "", "="*30, ""]

# News
for sq,title in [(f"\u7f8e\u80a1 \u4eca\u65e5 \u884c\u60c5 2026",f"\u4e00\u3001\u7f8e\u80a1\u5e02\u573a"),(f"A\u80a1 \u5927\u76d8 \u6700\u65b0",f"\u4e8c\u3001A\u80a1\u5e02\u573a"),(f"\u5b8f\u89c2\u7ecf\u6d4e \u8981\u95fb",f"\u4e09\u3001\u5b8f\u89c2\u7ecf\u6d4e")]:
    lines.append(f"\n{title}")
    for n in sc(sq,3):
        t = n.get("title","").strip()
        if t: lines.append(f"  {t}")

bd = os.path.dirname(__file__)
# Price
p = monitor([{"n":"iPhone 16 Pro","q":"iPhone 16 Pro \u4ef7\u683c \u6700\u65b0"},{"n":"MacBook Pro M4","q":"MacBook Pro M4 \u4ef7\u683c \u6700\u65b0"},{"n":"RTX 5090","q":"RTX 5090 \u663e\u5361 \u4ef7\u683c \u6700\u65b0"}],os.path.join(bd,"monitors","cache","price_cache.json"))
if p: lines.extend(["\n\u56db\u3001\u4ef7\u683c\u76d1\u63a7"]+p)

# Jobs
j = monitor([{"n":"Python\u5de5\u7a0b\u5e08","q":"Python\u5de5\u7a0b\u5e08 \u62db\u8058 \u5317\u4eac 2026"},{"n":"\u6570\u636e\u5206\u6790\u5e08","q":"\u6570\u636e\u5206\u6790\u5e08 \u62db\u8058 \u4e0a\u6d77 2026"},{"n":"AI\u5de5\u7a0b\u5e08","q":"AI\u5de5\u7a0b\u5e08 \u62db\u8058 \u6700\u65b0 2026"}],os.path.join(bd,"monitors","cache","jobs_cache.json"))
if j: lines.extend(["\n\u4e94\u3001\u5c97\u4f4d\u76d1\u63a7"]+j)

lines.append(f"\n{'='*30}\nFirecrawl | {TODAY}")
msg = "\n".join(lines)
print(msg)
if SC_KEY:
    d = json.dumps({"title": f"StockMini \u7efc\u5408\u65e5\u62a5 {TODAY}", "desp": msg}).encode()
    urllib.request.urlopen(urllib.request.Request(f"https://sctapi.ftqq.com/{SC_KEY}.send",data=d,headers={"Content-Type":"application/json"}),timeout=15)
    print("Sent!")
