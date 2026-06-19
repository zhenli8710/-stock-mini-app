import os, sys, datetime, urllib.request, json, re
sys.stdout.reconfigure(encoding="utf-8")

SC_KEY = os.environ.get("SERVERCHAN_KEY", "")
BN = "https://stock-mini-app-production.up.railway.app"
TODAY = datetime.date.today().strftime("%Y-%m-%d")
UA = "Mozilla/5.0"

# ── Direct data fetch (no Firecrawl) ──
def tencent_quote(codes):
    p = []
    for c in codes:
        if c.startswith(("6","9")): p.append(f"sh{c}")
        elif c.startswith("8"): p.append(f"bj{c}")
        else: p.append(f"sz{c}")
    req = urllib.request.Request(f"https://qt.gtimg.cn/q={','.join(p)}", headers={"User-Agent": UA})
    resp = urllib.request.urlopen(req, timeout=10).read().decode("gbk")
    r = {}
    for line in resp.strip().split(";"):
        if '"' not in line: continue
        v = line.split('"')[1].split("~")
        if len(v) < 49: continue
        c = v[2].strip()
        r[c] = {"name": v[1], "price": float(v[3]) if v[3] else 0, "chg": float(v[32]) if v[32] else 0}
    return r

def eastmoney_news(ps=30):
    url = f"https://np-weblist.eastmoney.com/comm/web/listCG?client=web&biz=web&type=0&page=1&pageSize={ps}&tag=all&ext=%7B%22pool%22%3A%22global%22%7D"
    d = json.loads(urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA,"Referer":"https://finance.eastmoney.com/"})).read())
    items = []
    for a in d.get("data",{}).get("list",[]):
        items.append({"time":a.get("showDate",""),"title":re.sub(r"<[^>]+>","",str(a.get("title","")))})
    return items

def ths_hot():
    url = f"http://zx.10jqka.com.cn/event/api/getharden/date/{datetime.date.today().strftime('%Y-%m-%d')}/orderby/date/orderway/desc/charset/GBK/"
    d = json.loads(urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA}),timeout=10).read())
    return d.get("data") or []

# ── Build report ──
lines = [f"StockMini 每日报告 | {TODAY}", "", "="*30, ""]

# 1. 全球财经要闻
lines.append("\n一、全球财经要闻")
news = eastmoney_news(10)
for n in news[:5]:
    lines.append(f"- {n.get('title','')}")

# 2. A股复盘
lines.append("\n二、A股复盘与开盘前必读\n")
idx = tencent_quote(["000001","399001","399006","000300"])
for name, code in [("上证指数","000001"),("深证成指","399001"),("创业板指","399006"),("沪深300","000300")]:
    if code in idx:
        d = idx[code]
        arrow = "📈" if d["chg"] >= 0 else "📉"
        lines.append(f"{arrow} {name}: {d['price']} ({d['chg']:+.2f}%)")

lines.append("\n【强势个股 TOP10】")
hot = ths_hot()
for s in hot[:10]:
    n = s.get("name",""); c = s.get("code",""); z = s.get("zhangfu",0); d = s.get("ddejingliang",0)
    reason = s.get("reason","")
    lines.append(f"  {n}({c}): {z:+.2f}% DDX={d} {reason[:30]}")

# 3. 全球重大新闻
lines.append("\n三、全球重大新闻")
for n in news[:8]:
    lines.append(f"- {n.get('title','')}")

# 4. 最新产品价格
lines.append("\n四、最新产品价格")
prices = tencent_quote(["000001","000300","sh600519","sh601857","sh600036"])
for name, code in [("上证指数","000001"),("沪深300","000300"),("贵州茅台","sh600519"),("中国石油","sh601857"),("招商银行","sh600036")]:
    if code in prices:
        d = prices[code]
        lines.append(f"- {name}: {d['price']} ({d['chg']:+.2f}%)")

lines.append(f"\n{'='*30}\na-stock-data | {TODAY}")
msg = "\n".join(lines)
print(msg)

# Push to WeChat via ServerChan
if SC_KEY:
    data = json.dumps({"title": f"StockMini 每日报告 {TODAY}", "desp": msg}).encode()
    req = urllib.request.Request(f"https://sctapi.ftqq.com/{SC_KEY}.send", data=data, headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
    print("✅ Sent!" if resp.get("code") == 0 else f"❌ Failed: {resp}")
