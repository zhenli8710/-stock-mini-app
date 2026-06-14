import urllib.request, json, datetime, os, sys, re
sys.stdout.reconfigure(encoding="utf-8")

KEY = os.environ.get("SERVERCHAN_KEY", "")
BN = "https://stock-mini-app-production.up.railway.app"

def sc(q, lim):
    r = urllib.request.Request(BN + "/api/search",
        data=json.dumps({"query": q, "limit": lim}).encode(),
        headers={"Content-Type": "application/json"})
    return (json.loads(urllib.request.urlopen(r, timeout=60).read())
            .get("data", {}).get("web", []))

def run():
    today = datetime.date.today()
    lines = [f"StockMini 感财日报 | {today}", "", "="*30, ""]
    
    # 一き取消废布
    lines.append("一、大星心受读明再明组")
    news = sc("stock market today closing S&P 500 Nasdaq Dow", 5)
    for n in news:
        t = n.get("title","").strip()
        desc = n.get("description","").strip()
        if t:
            lines.append(f"■ {t}")
            if desc and len(desc)>30:
                lines.append(f"  {desc[:180]}")
            lines.append("")
    
    # 二、这空个码
    lines.append("二、重要组 (AAPL / NVDA / TSLA")"
    for sym in ["AAPL","NVDA","TSLA"]:
        for n in sc(f"{sym} stock news",2):
            t = n.get("title","").strip()
            if t and sym.lower() in t.lower():
                lines.append(f"■ {t}")
                desc = n.get("description","").strip()
                if desc and len(desc)>30:
                    lines.append(f"  {desc[:180]}")
                lines.append("")
    
    # 三、完步要闻
    lines.append("三、宏观要闻")
    for n in sc("Federal Reserve economy inflation GDP",4):
        t = n.get("title","").strip()
        if t:
            lines.append(f"■ {t}")
            desc = n.get("description","").strip()
            if desc and len(desc)>30:
                lines.append(f"  {desc[:180]}")
            lines.append("")
    
    # 四、中止/银族
    lines.append("四、中国请明信息")
    for n in sc("China stock market Asia economy Hong Kong",4):
        t = n.get("title","").strip()
        if t:
            lines.append(f"■ {t}")
            desc = n.get("description","").strip()
            if desc and len(desc)>30:
                lines.append(f"  {desc[:180]}")
            lines.append("")
    
    lines.append("="*30)
    lines.append(f"数据改序: Firecrawl | {today}")
    return "\n".join(lines)

if __name__ == "__main__":
    r = run()
    print(r)
    print()
    if KEY:
        data = json.dumps({"title": "StockMini 财经日报", "desp": r}).encode()
        req = urllib.request.Request(f"https://sctapi.ftqq.com/{KEY}.send", data=data, headers={"Content-Type": "application/json"})
        resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
        if resp.get("code") == 0:
            print("OK: Sent to WeChat")
        else:
            print("Fail:", resp.get("message",""))
    else:
        print("No SERVERCHAN_KEY")
