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


@app.get("/api/health")
async def health():
    return {"status": "ok", "firecrawl_configured": bool(FIRECRAWL_API_KEY)}


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
