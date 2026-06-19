import os, sys, datetime, urllib.request, json
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

# 1
lines.append("\n\u4e00\u3001\u5168\u7403\u8d22\u7ecf\u8981\u95fb")
for n in sc("\u5168\u7403\u8d22\u7ecf\u8981\u95fb \u6700\u65b0 \u91cd\u8981 2026",5):
    t=n.get("title","").strip(); u=n.get("url","")
    if t: lines.append(f"- [{t}]({u})")

# 2 A\u80a1\u590d\u76d8
lines.append("\n\u4e8c\u3001A\u80a1\u590d\u76d8\u4e0e\u5f00\u76d8\u524d\u5fc5\u8bfb\n")
lines.append("\u3010\u5927\u76d8\u6570\u636e\u3011")
for q,nm in [("\u4e0a\u8bc1\u6307\u6570 \u4eca\u5f00 \u6700\u9ad8 \u6700\u4f4e \u6210\u4ea4\u989d \u4e0a\u6da8\u5bb6\u6570 \u884c\u60c5","\u4e0a\u8bc1\u6307\u6570"),("\u6df1\u8bc1\u6210\u6307 \u4eca\u5f00 \u6700\u9ad8 \u6700\u4f4e \u6210\u4ea4\u989d \u884c\u60c5","\u6df1\u8bc1\u6210\u6307"),("\u521b\u4e1a\u677f\u6307 \u4eca\u5f00 \u6700\u9ad8 \u6700\u4f4e \u884c\u60c5","\u521b\u4e1a\u677f\u6307")]:
    lines.append(f"\u25b6 {nm}")
    for n in sc(q,2):
        desc=(n.get("description","") or "")[:200]
        if "\u4eca\u5f00" in desc or "\u6700\u9ad8" in desc or "\u4e0a\u6da8" in desc:
            lines.append(f"  {desc}")

lines.append("\n\u3010\u9886\u6da8\u677f\u5757\u3011")
for n in sc("\u5927\u76d8\u5206\u6790 \u4e1c\u65b9\u8d22\u5bcc A\u80a1 \u677f\u5757",2):
    desc=(n.get("description","") or "")[:200]
    if "\u6da8\u5e45" in desc or "\u677f\u5757" in desc:
        lines.append(f"  {desc}")

lines.append("\n\u3010\u5f00\u76d8\u524d\u5fc5\u8bfb\u3011")
for n in sc("\u5f00\u76d8\u524d\u5fc5\u8bfb A\u80a1 \u91cd\u8981 \u6d88\u606f 2026",5):
    t=n.get("title","").strip(); u=n.get("url","")
    desc=(n.get("description","") or "")[:80]
    if t: lines.append(f"- [{t}]({u})")
    if desc: lines.append(f"  {desc}")

lines.append("\n\u3010\u91cd\u70b9\u5173\u6ce8\u3011")
for n in sc("A\u80a1 \u4e2a\u80a1 \u63a8\u8350 \u5173\u6ce8 \u70ed\u70b9 2026",5):
    t=n.get("title","").strip(); u=n.get("url","")
    desc=(n.get("description","") or "")[:120]
    if t: lines.append(f"- [{t}]({u})")
    if desc: lines.append(f"  {desc}")
lines.append("\n*\u4ec5\u4f9b\u53c2\u8003\uff0c\u4e0d\u6784\u6210\u6295\u8d44\u5efa\u8bae*")

# 3
lines.append("\n\u4e09\u3001\u5168\u7403\u91cd\u5927\u65b0\u95fb")
for n in sc("\u5168\u7403\u91cd\u5927\u65b0\u95fb \u56fd\u9645 \u6700\u65b0 2026",5):
    t=n.get("title","").strip(); u=n.get("url","")
    if t: lines.append(f"- [{t}]({u})")

# 4
lines.append("\n\u56db\u3001AI\u5de5\u5177\u5bfc\u822a")
lines.append(f"- [\u70b9\u51fb\u8bbf\u95ee aichagpt.com](https://aichagpt.com)")

# 5
lines.append("\n\u4e94\u3001\u6700\u65b0\u4ea7\u54c1\u4ef7\u683c")
for nm,q in [("iPhone 16 Pro","iPhone 16 Pro \u4ef7\u683c \u6700\u65b0"),("MacBook Pro M4","MacBook Pro M4 \u4ef7\u683c \u6700\u65b0"),("\u534e\u4e3aMate 70","\u534e\u4e3aMate 70 \u4ef7\u683c \u6700\u65b0"),("\u534e\u4e3aPura 80","\u534e\u4e3aPura 80 \u4ef7\u683c \u6700\u65b0")]:
    for n in sc(q,2):
        t=n.get("title","").strip(); u=n.get("url","")
        if t: lines.append(f"- **{nm}**: [{t}]({u})")

lines.append(f"\n{'='*30}\n\u5408\u4f5cV\uff1aLiZChary\nFirecrawl | {TODAY}")
msg = "\n".join(lines)
print(msg)
if SC_KEY:
    d=json.dumps({"title":f"StockMini \u6bcf\u65e5\u62a5\u544a {TODAY}","desp":msg}).encode()
    urllib.request.urlopen(urllib.request.Request(f"https://sctapi.ftqq.com/{SC_KEY}.send",data=d,headers={"Content-Type":"application/json"}),timeout=15)
    print("Sent!")
