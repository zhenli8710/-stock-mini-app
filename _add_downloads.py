import os, re

base = r"C:\Users\Administrator\stock-mini-app\seo-site\tool"
downloads = {
    "chatgpt.html": ("https://chatgpt.com", "ChatGPT 官网", "Web端直接使用，无需下载，注册即可。"),
    "claude.html": ("https://claude.ai", "Claude 官网", "Web端直接使用，支持桌面版。"),
    "cursor.html": ("https://cursor.sh", "Cursor 下载", "支持Windows/Mac/Linux桌面客户端。"),
    "midjourney.html": ("https://midjourney.com", "Midjourney 官网", "通过Discord使用，需注册Discord账号。"),
    "sora.html": ("https://sora.com", "Sora 官网", "通过OpenAI平台使用，需要Plus/Pro订阅。"),
    "notion-ai.html": ("https://notion.so", "Notion 下载", "支持Web、Windows、Mac、iOS、Android。"),
}

for filename, (url, label, desc) in downloads.items():
    fp = os.path.join(base, filename)
    if not os.path.exists(fp): continue
    c = open(fp, "r", encoding="utf-8").read()
    # Add download section after pricing table
    dl_html = f'''<div class="download-box">
    <h3>获取方式</h3>
    <p>{desc}</p>
    <a href="{url}" class="dl-btn" target="_blank" rel="noopener">⬇ {label}</a>
</div>'''
    # Insert before the pros section or at the end of article
    c = c.replace('<div class="pros"', dl_html + '\n<div class="pros"', 1)
    open(fp, "w", encoding="utf-8").write(c)
    print(f"Updated {filename}")
print("All done")
print("CSS needs: .download-box style")
