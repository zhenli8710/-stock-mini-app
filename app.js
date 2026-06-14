// StockMini - Telegram Mini App
(function() {
    'use strict';

    // Telegram Web App init
    let tg = null;
    try {
        tg = window.Telegram?.WebApp;
        if (tg) {
            tg.ready();
            tg.expand();
            tg.setHeaderColor ? tg.setHeaderColor('#0f1929') : null;
            tg.setBackgroundColor ? tg.setBackgroundColor('#0f1929') : null;
        }
    } catch(e) { console.log('Not in Telegram'); }

    // Config
    const BACKEND_URL = window.location.origin;
    const FIRECRAWL_API_URL = 'https://api.firecrawl.dev/v2';
    let firecrawlApiKey = '';

    // DOM refs
    const newsList = document.getElementById('news-list');
    const resultSection = document.getElementById('result-section');
    const resultContent = document.getElementById('result-content');
    const resultTitle = document.getElementById('result-title');
    const newsCount = document.getElementById('news-count');

    // Toast
    let toastTimer = null;
    window.showToast = function(msg) {
        const t = document.getElementById('toast');
        t.textContent = msg;
        t.classList.add('show');
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => t.classList.remove('show'), 2500);
    };

    // Try to load API key
    async function loadConfig() {
        try {
            const resp = await fetch(`${BACKEND_URL}/api/config`);
            if (resp.ok) {
                const cfg = await resp.json();
                if (cfg.apiKey) firecrawlApiKey = cfg.apiKey;
            }
        } catch(e) {}
    }

    // Set API key (from Telegram init data or manually)
    window.setApiKey = function(key) {
        firecrawlApiKey = key;
        localStorage.setItem('fc_api_key', key);
        showToast('API key set');
    };

    // Load key from localStorage
    const saved = localStorage.getItem('fc_api_key');
    if (saved) firecrawlApiKey = saved;

    // --- Firecrawl API calls ---

    async function fcSearch(query, limit = 8) {
        // Try backend first
        try {
            const resp = await fetch(`${BACKEND_URL}/api/search`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ query, limit })
            });
            if (resp.ok) return await resp.json();
        } catch(e) {}

        // Fallback: direct API
        if (!firecrawlApiKey) throw new Error('No API key configured');
        const resp = await fetch(`${FIRECRAWL_API_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${firecrawlApiKey}`
            },
            body: JSON.stringify({ query, limit, scrapeOptions: { formats: ['markdown'] } })
        });
        if (!resp.ok) throw new Error(`API error: ${resp.status}`);
        return await resp.json();
    }

    async function fcScrape(url) {
        if (!firecrawlApiKey) throw new Error('No API key configured');
        const resp = await fetch(`${FIRECRAWL_API_URL}/scrape`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${firecrawlApiKey}`
            },
            body: JSON.stringify({ url, formats: ['markdown'], onlyMainContent: true })
        });
        if (!resp.ok) throw new Error(`Scrape error: ${resp.status}`);
        return await resp.json();
    }

    // --- UI ---

    function formatTimeAgo(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        const now = new Date();
        const diff = Math.floor((now - d) / 1000);
        if (diff < 60) return 'just now';
        if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
        return `${Math.floor(diff/86400)}d ago`;
    }

    function renderNews(results) {
        if (!results || results.length === 0) {
            newsList.innerHTML = '<div class="loading">No news found</div>';
            newsCount.textContent = '0';
            return;
        }
        newsCount.textContent = results.length;
        newsList.innerHTML = results.map((item, idx) => {
            const title = item.title || 'Untitled';
            const url = item.url || '#';
            const desc = (item.description || '').slice(0, 200);
            const date = item.date || '';
            const source = item.source || new URL(url).hostname || '';
            return `
                <div class="news-item" onclick="openArticle('${url.replace(/'/g, "\\'")}', '${title.replace(/'/g, "\\'")}')" style="animation-delay:${idx * 0.03}s">
                    <div class="news-title">${title}</div>
                    <div class="news-meta"><span>${source}</span>${date ? '<span>'+formatTimeAgo(date)+'</span>' : ''}</div>
                    ${desc ? '<div class="news-desc">'+desc+'</div>' : ''}
                </div>
            `;
        }).join('');
    }

    window.openArticle = async function(url, title) {
        if (tg) {
            tg.showAlert(`Loading: ${title}...`);
        }
        resultTitle.textContent = title;
        resultContent.innerHTML = '<div class="loading">Loading article...</div>';
        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth' });

        // Try to scrape
        try {
            const data = await fcScrape(url);
            const md = data?.data?.markdown || data?.markdown || '';
            if (md) {
                // Simple markdown to HTML conversion
                const html = md
                    .slice(0, 3000)
                    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
                    .replace(/## (.+)/g, '<strong>$1</strong>')
                    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\n\n/g, '</p><p>')
                    .replace(/\n/g, '<br>');
                resultContent.innerHTML = `<p>${html}</p><p style="margin-top:16px;font-size:11px;color:#666"><a href="${url}" target="_blank" style="color:#4f9cf7">Read full article →</a></p>`;
            } else {
                resultContent.innerHTML = `<p>Full content not available.</p><p style="margin-top:12px"><a href="${url}" target="_blank" style="color:#4f9cf7">Open in browser →</a></p>`;
            }
        } catch(e) {
            resultContent.innerHTML = `<p>Could not load article.</p><p style="margin-top:12px"><a href="${url}" target="_blank" style="color:#4f9cf7">Open in browser →</a></p>`;
        }
    };

    window.closeResult = function() {
        resultSection.style.display = 'none';
    };

    // --- Search ---

    window.searchStock = async function() {
        const q = document.getElementById('stock-input').value.trim();
        if (!q) return;
        showToast(`Searching: ${q}...`);
        try {
            const data = await fcSearch(q + ' stock market news');
            const results = data?.data?.web || data?.web || data?.data || [];
            renderNews(results);
        } catch(e) {
            showToast('Search failed: ' + e.message);
        }
    };

    window.quickSearch = async function(symbol) {
        document.getElementById('stock-input').value = symbol;
        showToast(`Loading ${symbol} news...`);
        try {
            const data = await fcSearch(`${symbol} stock news`, 8);
            const results = data?.data?.web || data?.web || data?.data || [];
            renderNews(results);
        } catch(e) {
            showToast('Failed: ' + e.message);
        }
    };

    // --- Market Data ---

    async function updateMarketData() {
        try {
            const data = await fcSearch('S&P 500 NASDAQ Dow Jones market today', 1);
            // Update from search result descriptions
            if (data?.data?.web?.[0]?.description) {
                const desc = data.data.web[0].description;
                // Try to extract index values
                // In a production app, this would use a proper market data API
            }
        } catch(e) {}
    }

    // --- Load Latest News ---

    window.loadLatestNews = async function() {
        newsList.innerHTML = '<div class="loading">Loading latest news...</div>';
        try {
            const data = await fcSearch('stock market latest news today', 10);
            const results = data?.data?.web || data?.web || data?.data || [];
            renderNews(results);
        } catch(e) {
            newsList.innerHTML = '<div class="loading">Could not load news. Click to retry.</div>';
        }
    };

    window.refreshMarket = async function() {
        showToast('Refreshing...');
        try {
            const data = await fcSearch('S&P 500 NASDAQ Dow Jones current level', 3);
            const results = data?.data?.web || data?.web || data?.data || [];
            if (results[0]?.description) {
                const desc = results[0].description;
                // Extract numbers
                const nums = desc.match(/([0-9,.]+)/g);
                const sp = document.getElementById('sp500');
                const na = document.getElementById('nasdaq');
                const dj = document.getElementById('djia');
                if (nums) {
                    if (nums[0]) { sp.textContent = nums[0]; sp.className = 'value up'; }
                    if (nums[1]) { na.textContent = nums[1]; na.className = 'value up'; }
                    if (nums[2]) { dj.textContent = nums[2]; dj.className = 'value up'; }
                }
            }
        } catch(e) {}
    };

    // --- Init ---
    loadConfig().then(() => loadLatestNews());

})();
