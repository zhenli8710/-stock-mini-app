# StockMini - Telegram Mini App Setup Guide

## Overview
StockMini is a Telegram Mini App for stock market news and research, powered by Firecrawl API.

## Project Structure
stock-mini-app/
  index.html        # Main app UI (Telegram Web App SDK)
  style.css         # Dark theme styling
  app.js            # Frontend logic
  backend.py        # FastAPI backend (proxies Firecrawl API)
  requirements.txt  # Python dependencies
  render.yaml       # Render deployment config

## Quick Start (Local Dev)
```
cd stock-mini-app
$env:FIRECRAWL_API_KEY = "fc-5aac048424bc4a82809de7c22cdb3eb7"
pip install -r requirements.txt
python backend.py
```
Open http://localhost:8000 in browser.

## Deploy to Render (Free)
1. Push to GitHub
2. Go to dashboard.render.com -> New + -> Blueprint
3. Connect repo, set FIRECRAWL_API_KEY env var
4. Deploy! Get URL: https://stock-mini-app.onrender.com

## Telegram Bot Setup
1. Open @BotFather -> /newbot -> name StockMini
2. Save bot token
3. /mybots -> Bot Settings -> Menu Button -> Set URL to your deployed URL
4. /setdomain -> your-app.onrender.com
5. Open bot in Telegram, tap Launch button

## Env Vars
FIRECRAWL_API_KEY - Required - Your Firecrawl API key
PORT - Optional - Server port (default 8000)
