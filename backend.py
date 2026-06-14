#!/usr/bin/env python3
"""StockMini Backend Server - proxy to Firecrawl API"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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


# Serve frontend
static_dir = os.path.join(os.path.dirname(__file__), ".")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend:app", host="0.0.0.0", port=port, reload=False)
