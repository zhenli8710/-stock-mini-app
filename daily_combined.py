import os, json, sys, datetime, urllib.request
sys.stdout.reconfigure(encoding="utf-8")
SC_KEY = os.environ.get("SERVERCHAN_KEY", "")
BN = "https://stock-mini-app-production.up.railway.app"
TODAY = datetime.date.today()

def sc(q, li=3):
    try:
        r = urllib.request.Request(BN+"/api/search",data=json.dumps({"query":q,"limit":li}).encode(),headers={"Content-Type":"application/json"})
        d = json.loads(urllib.request.urlopen(r,timeout=60).read())
        return d.get("data",{}).get("web",[]) or []
    except: return []

def monitor(items, cf):
    old = {}
    if os.path.exists(cf):
        try: old = json.load(open(cf,"r",encoding="utf-8"))
        except: pass
    nd = {}
    lines = []
    for item in items:
        r = sc(item["q"],3)
        entries = [(n.get("title","").strip(), n.get("url","")) for n in r if n.get("title")]
        nd[item["n"]] = entries
        ot = old.get(item["n"],[])
        status = "首" if not ot else ("新" if entries != ot else "·")
        lines.append(f"  {status} {item['n']}: {len(entries)}条")
        for t,u in entries[:2]:
            lines.append(f"    {t}")
            if u: lines.append(f"    {u}")
    json.dump(nd,open(cf,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    return lines

lines = [f"StockMini \u7efc\u5408\u65e5\u62a5 | {TODAY}", "", "="*20, ""]

for sq,title in [("\u7f8e\u80a1 \u884c\u60c5 \u4eca\u65e5 2026","\u4e00\u3001\u7f8e\u80a1\u5e02\u573a"),("A\u80a1 \u5927\u76d8 \u6700\u65b0 2026","\u4e8c\u3001A\u80a1\u5e02\u573a"),("\u5b8f\u89c2\u7ecf\u6d4e \u8981\u95fb 2026","\u4e09\u3001\u5b8f\u89c2\u7ecf\u6d4e")]:
    lines.append(f"\n{title}")
    for n in sc(sq,4):
        t=n.get("title","").strip()
        u=n.get("url","")
        if t:
            lines.append(f"  {t}")
            if u: lines.append(f"  {u}")

bd = os.path.dirname(__file__)
lines.append("\n\u56db\u3001\u4ef7\u683c\u76d1\u63a7")
lines.extend(monitor([
    {"n":"iPhone 16 Pro","q":"iPhone 16 Pro \u4ef7\u683c \u6700\u65b0"},
    {"n":"MacBook Pro M4","q":"MacBook Pro M4 \u4ef7\u683c \u6700\u65b0"},
    {"n":"RTX 5090","q":"RTX 5090 \u663e\u5361 \u4ef7\u683c \u6700\u65b0"}
],os.path.join(bd,"monitors","cache","price_cache.json")))

lines.append("\n\u4e94\u3001\u5c97\u4f4d\u76d1\u63a7")
lines.extend(monitor([
    {"n":"Python\u5de5\u7a0b\u5e08","q":"Python\u5de5\u7a0b\u5e08 \u62db\u8058 \u5317\u4eac 2026"},
    {"n":"\u6570\u636e\u5206\u6790\u5e08","q":"\u6570\u636e\u5206\u6790\u5e08 \u62db\u8058 \u4e0a\u6d77 2026"},
    {"n":"AI\u5de5\u7a0b\u5e08","q":"AI\u5de5\u7a0b\u5e08 \u62db\u8058 \u6700\u65b0 2026"}
],os.path.join(bd,"monitors","cache","jobs_cache.json")))

lines.append(f"\n{'='*20}\nFirecrawl | {TODAY}")
msg = "\n".join(lines)
print(msg)
if SC_KEY:
    d = json.dumps({"title": f"StockMini \u7efc\u5408\u65e5\u62a5 {TODAY}", "desp": msg}).encode()
    urllib.request.urlopen(urllib.request.Request(f"https://sctapi.ftqq.com/{SC_KEY}.send",data=d,headers={"Content-Type":"application/json"}),timeout=15)
    print("Sent!")
