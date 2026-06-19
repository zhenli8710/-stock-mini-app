import os, sys, datetime, urllib.request, json, re
sys.stdout.reconfigure(encoding="utf-8")
SC_KEY = os.environ.get("SERVERCHAN_KEY", "")
BN = "https://stock-mini-app-production.up.railway.app"
TODAY = datetime.date.today().strftime("%Y-%m-%d")

def sc(q, li=5):
    try:
        r = urllib.request.Request(BN+"/api/search",data=json.dumps({"query":q,"limit":li}).encode(),headers={"Content-Type":"application/json"})
        d = json.loads(urllib.request.urlopen(r,timeout=60).read())
        return d.get("data",{}).get("web",[]) or []
    except: return []

lines = [f"StockMini \u6bcf\u65e5\u62a5\u544a | {TODAY}", "", "="*30, ""]

# Section 1
lines.append("\u4e00\u3001\u5168\u7403\u8d22\u7ecf\u8981\u95fb")
for n in sc("\u5168\u7403\u8d22\u7ecf\u8981\u95fb \u6700\u65b0 \u91cd\u8981 2026",5):
    t=n.get("title","").strip()
    u=n.get("url","")
    if t: lines.append(f"- [{t}]({u})")
lines.append("")

# Section 2 \u2014 A\u80a1\u590d\u76d8+\u5f00\u76d8\u524d\u5fc5\u8bfb
lines.append("\u4e8c\u3001A\u80a1\u590d\u76d8\u4e0e\u5f00\u76d8\u524d\u5fc5\u8bfb")
lines.append("")
# Index data
lines.append("\u3010\u5927\u76d8\u6570\u636e\u3011")
for q in ["\u4e0a\u8bc1\u6307\u6570 \u6700\u65b0 \u6536\u76d8 \u6da8\u8dcc", "\u6df1\u8bc1\u6210\u6307 \u6700\u65b0 \u6536\u76d8", "\u521b\u4e1a\u677f\u6307 \u6700\u65b0 \u6536\u76d8"]:
    for n in sc(q,2):
        t=n.get("title","").strip()
        u=n.get("url","")
        d=(n.get("description","") or "")[:80]
        if t: lines.append(f"- {t}")
        if d: lines.append(f"  {d}")
lines.append("")
# Hot sectors
lines.append("\u3010\u70ed\u70b9\u677f\u5757\u3011")
for n in sc("A\u80a1 \u70ed\u70b9 \u677f\u5757 \u6da8\u5e45 \u4eca\u65e5",4):
    t=n.get("title","").strip()
    u=n.get("url","")
    d=(n.get("description","") or "")[:100]
    if t: lines.append(f"- [{t}]({u})")
    if d: lines.append(f"  {d}")
lines.append("")
# Pre-market
lines.append("\u3010\u5f00\u76d8\u524d\u5fc5\u8bfb\u3011")
for n in sc("\u5f00\u76d8\u524d\u5fc5\u8bfb A\u80a1 \u91cd\u8981\u6d88\u606f",5):
    t=n.get("title","").strip()
    u=n.get("url","")
    d=(n.get("description","") or "")[:80]
    if t: lines.append(f"- [{t}]({u})")
    if d: lines.append(f"  {d}")
lines.append("")

# Section 3
lines.append("\u4e09\u3001\u5168\u7403\u91cd\u5927\u65b0\u95fb")
for n in sc("\u5168\u7403\u91cd\u5927\u65b0\u95fb \u56fd\u9645 \u6700\u65b0 2026",5):
    t=n.get("title","").strip()
    u=n.get("url","")
    if t: lines.append(f"- [{t}]({u})")
lines.append("")

# Section 4
lines.append("\u56db\u3001AI\u5de5\u5177\u5bfc\u822a")
lines.append(f"- [\u70b9\u51fb\u8bbf\u95ee aichagpt.com](https://aichagpt.com)")
lines.append("")

# Section 5
lines.append("\u4e94\u3001\u6700\u65b0\u4ea7\u54c1\u4ef7\u683c")
for nm,q in [("iPhone 16 Pro","iPhone 16 Pro \u4ef7\u683c \u6700\u65b0"),("MacBook Pro M4","MacBook Pro M4 \u4ef7\u683c \u6700\u65b0"),("\u534e\u4e3aMate 70","\u534e\u4e3aMate 70 \u4ef7\u683c \u6700\u65b0"),("\u534e\u4e3aPura 80","\u534e\u4e3aPura 80 \u4ef7\u683c \u6700\u65b0")]:
    for n in sc(q,2):
        t=n.get("title","").strip()
        u=n.get("url","")
        if t: lines.append(f"- **{nm}**: [{t}]({u})")
lines.append("")

lines.append(f"\n{'='*30}\n\u5408\u4f5cV\uff1aLiZChary\nFirecrawl | {TODAY}")
msg = "\n".join(lines)
print(msg)
if SC_KEY:
    d=json.dumps({"title":f"StockMini \u6bcf\u65e5\u62a5\u544a {TODAY}","desp":msg}).encode()
    urllib.request.urlopen(urllib.request.Request(f"https://sctapi.ftqq.com/{SC_KEY}.send",data=d,headers={"Content-Type":"application/json"}),timeout=15)
    print("Sent!")
