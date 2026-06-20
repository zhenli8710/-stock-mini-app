#!/usr/bin/env python3
"""StockMini Backend Server - proxy to Firecrawl API"""

import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx
import uvicorn

app = FastAPI(title="StockMini API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")
FIRECRAWL_V2_URL = "https://api.firecrawl.dev/v2"


class SearchRequest(BaseModel):
    query: str
    limit: int = 8


class ScrapeRequest(BaseModel):
    url: str


@app.get("/api/config")
async def get_config():
    has_key = bool(FIRECRAWL_API_KEY)
    return {"configured": has_key, "apiKey": FIRECRAWL_API_KEY if has_key else ""}


@app.post("/api/search")
async def search(req: SearchRequest):
    if not FIRECRAWL_API_KEY:
        raise HTTPException(status_code=400, detail="API key not configured")
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{FIRECRAWL_V2_URL}/search",
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"},
            json={"query": req.query, "limit": req.limit},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


@app.post("/api/scrape")
async def scrape(req: ScrapeRequest):
    if not FIRECRAWL_API_KEY:
        raise HTTPException(status_code=400, detail="API key not configured")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{FIRECRAWL_V2_URL}/scrape",
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"},
            json={"url": req.url, "formats": ["markdown"], "onlyMainContent": True},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


@app.post("/api/fetch")
async def fetch_url(req: ScrapeRequest):
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(req.url, headers={"User-Agent": "Mozilla/5.0"})
        return {"html": resp.text, "status": resp.status_code}

@app.get("/api/health")
async def health():
    return {"status": "ok", "firecrawl_configured": bool(FIRECRAWL_API_KEY)}


import re, urllib.request, json as _json

# ── Stock data API (no Firecrawl needed) ──
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def _tq(codes):
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
        r[c] = {"name": v[1], "price": float(v[3]) if v[3] else 0, "chg": float(v[32]) if v[32] else 0,
                 "high": float(v[33]) if v[33] else 0, "low": float(v[34]) if v[34] else 0,
                 "amount_wan": float(v[37]) if v[37] else 0, "turnover": float(v[38]) if v[38] else 0,
                 "mcap_yi": float(v[44]) if v[44] else 0, "fmcap_yi": float(v[45]) if v[45] else 0}
    return r

def _ths_hot():
    url = f"http://zx.10jqka.com.cn/event/api/getharden/date/{__import__('datetime').date.today().strftime('%Y-%m-%d')}/orderby/date/orderway/desc/charset/GBK/"
    d = _json.loads(urllib.request.urlopen(urllib.request.Request(url), timeout=10).read())
    return d.get("data") or []

def _em_news(ps=30):
    url = f"https://np-weblist.eastmoney.com/comm/web/listCG?client=web&biz=web&type=0&page=1&pageSize={ps}&tag=all&ext=%7B%22pool%22%3A%22global%22%7D"
    d = _json.loads(urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA,"Referer":"https://finance.eastmoney.com/"})).read())
    items = []
    for a in d.get("data",{}).get("list",[]):
        items.append({"time":a.get("showDate",""),"title":re.sub(r"<[^>]+>","",str(a.get("title","")))})
    return items

@app.get("/api/stock/news")
async def stock_news():
    return {"items": _em_news(20)}

@app.get("/api/stock/review")
async def stock_review():
    idx = _tq(["000001","399001","399006","000300"])
    hot = _ths_hot()
    return {"indexes": idx, "hot_stocks": hot[:15]}

@app.get("/api/stock/prices")
async def stock_prices():
    q = _tq(["000001","000300","399001","399006","sh600519","sh601857"])
    return q

@app.get("/api/stock/hot")
async def stock_hot():
    return {"items": _ths_hot()[:20]}
import threading, json as _json
from datetime import datetime, timedelta

# ── WeChat auto-send at 8:00 AM daily ──
SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY", "SCT364214Tj8zj8ZrbAVCj3O8lgywlRKeb")

def _wechat_push(title, content):
    """通过 Server酱 推送微信消息"""
    import urllib.request
    data = _json.dumps({"title": title, "desp": content}).encode()
    req = urllib.request.Request(f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send",
        data=data, headers={"Content-Type": "application/json"})
    try:
        resp = _json.loads(urllib.request.urlopen(req, timeout=15).read())
        return resp.get("code") == 0
    except: return False

def _daily_report():
    """生成每日复盘报告并推送微信"""
    try:
        idx = _tq(["000001","399001","399006","000300"])
        hot = _ths_hot()
        news = _em_news(8)
        today = datetime.now().strftime("%Y-%m-%d")
        
        lines = [f"📊 StockMini 每日复盘 {today}", "", "━"*20]
        
        # 大盘指数
        for name, code in [("上证指数","000001"),("深证成指","399001"),("创业板指","399006"),("沪深300","000300")]:
            if code in idx:
                d = idx[code]
                a = "📈" if d["chg"] >= 0 else "📉"
                lines.append(f"{a} {name}: {d['price']} ({d['chg']:+.2f}%)")
        
        # 强势个股
        if hot:
            lines.append("", "🔥 强势个股 TOP10:")
            for s in hot[:10]:
                n = s.get("name",""); c = s.get("code",""); z = s.get("zhangfu",0)
                lines.append(f"  {n}({c}): {z:+.2f}%")
        
        # 财经要闻
        if news:
            lines.append("", "📰 财经要闻:")
            for n in news[:5]:
                lines.append(f"  · {n.get('title','')}")
        
        lines.append("", "━"*20, "推送: a-stock-data | Server酱")
        msg = "\n".join(lines)
        
        ok = _wechat_push(f"StockMini 复盘 {today}", msg)
        print(f"[WeChat] Report sent: {ok}")
    except Exception as e:
        print(f"[WeChat] Error: {e}")

def _scheduler():
    """每天8:00运行复盘报告"""
    while True:
        now = datetime.now()
        target = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        wait = (target - now).total_seconds()
        time.sleep(wait)
        _daily_report()

# Start scheduler
t = threading.Thread(target=_scheduler, daemon=True)
t.start()
print("[OK] WeChat scheduler started (8:00 AM daily)")
@app.api_route("/{path:path}", methods=["GET"])
async def serve_pages(path: str, request: Request):
    host = request.headers.get("host", "")
    base = os.path.dirname(__file__)
    if "aichagpt" in host or "aichatgpt" in host:
        sp = os.path.join(base, "seo-site", path or "index.html")
        if path == "" or path == "/":
            sp = os.path.join(base, "seo-site", "index.html")
        if os.path.isfile(sp):
            return FileResponse(sp)
        return FileResponse(os.path.join(base, "seo-site", "index.html"))
    sp = os.path.join(base, path or "index.html")
    if path == "" or path == "/" or not path:
        return FileResponse(os.path.join(base, "stock-app.html"))
    if os.path.isfile(sp):
        return FileResponse(sp)
    return FileResponse(os.path.join(base, "stock-app.html"))

# Serve frontend
static_dir = os.path.join(os.path.dirname(__file__), ".")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend:app", host="0.0.0.0", port=port, reload=False)


