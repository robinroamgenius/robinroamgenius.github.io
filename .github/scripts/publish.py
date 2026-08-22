import os
import glob
from datetime import datetime

def main():
    drafts_dir = "drafts"
    posts_dir = "posts"
    
    os.makedirs(drafts_dir, exist_ok=True)
    os.makedirs(posts_dir, exist_ok=True)
    
    draft_files = sorted(glob.glob(os.path.join(drafts_dir, "*.md")))
    
    if not draft_files:
        print("Zadne nove clanky v /drafts.")
        return
        
    next_draft = draft_files[0]
    filename = os.path.basename(next_draft)
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Vytvoreni cisteho jmena pro HTML soubor
    html_filename = filename.replace(".md", ".html")
    if not html_filename.startswith(today_str):
        html_filename = f"{today_str}-{html_filename}"
        
    target_path = os.path.join(posts_dir, html_filename)
    
    with open(next_draft, "r", encoding="utf-8") as f:
        md_content = f.read()
        
    # Jednoducha konverze zakladniho markdownu na HTML bez externich knihoven
    html_content = md_content
    html_content = html_content.replace("\n# ", "\n<h1>")
    html_content = html_content.replace("\n## ", "\n<h2>")
    html_content = html_content.replace("\n### ", "\n<h3>")
    
    # Zabaleni do pekne sablony
    full_html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Článek | RoamGenius</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <header><a href="../index.html" style="color:white; text-decoration:none;">&larr; RoamGenius Home</a></header>
    <main style="max-width:750px; margin:40px auto; padding:0 20px;">
        {html_content}
    </main>
</body>
</html>"""

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    os.remove(next_draft)
    print(f"Publikovano: {html_filename}")
    
    # Aktualizace indexu a RSS
    generate_index_and_rss()

def generate_index_and_rss():
    post_files = sorted(glob.glob("posts/*.html"), reverse=True)
    posts_list_html = ""
    rss_items = ""
    
    for pf in post_files:
        filename = os.path.basename(pf)
        date_part = filename[:10]
        title_part = filename[11:-5].replace("-", " ").title()
        
        posts_list_html += f"""
        <article style="background:white; padding:20px; margin-bottom:20px; border-radius:8px;">
            <span style="color:#888;">{date_part}</span>
            <h2><a href="posts/{filename}" style="color:#1a2a3a; text-decoration:none;">{title_part}</a></h2>
        </article>
        """
        
        rss_items += f"""
        <item>
            <title>{title_part}</title>
            <link>https://github.io{filename}</link>
            <guid>https://github.io{filename}</guid>
            <pubDate>{date_part}T09:00:00Z</pubDate>
            <description>Novy clanek na RoamGenius</description>
        </item>
        """
        
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"<html><head><link rel='stylesheet' href='style.css'></head><body style='background:#f9f9f9; font-family:sans-serif;'><header style='background:#1a2a3a; color:white; padding:40px; text-align:center;'><h1>RoamGenius</h1><p>Trading & Cestovani na autopilotu</p></header><main style='max-width:750px; margin:20px auto;'>{posts_list_html}</main></body></html>")

    with open("rss.xml", "w", encoding="utf-8") as f:
        f.write(f"<?xml version='1.0' encoding='UTF-8' ?><rss version='2.0'><channel><title>RoamGenius</title><link>https://github.io</link><description>Trading a Cestovani</description>{rss_items}</channel></rss>")

if __name__ == "__main__":
    main()
