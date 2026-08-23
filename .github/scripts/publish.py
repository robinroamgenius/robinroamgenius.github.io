import os
import glob
import re
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
    
    # Vytvoreni krasne SEO friendly adresy bez zbytecnych znaku
    seo_name = filename.lower().replace(".md", ".html")
    seo_name = re.sub(r'[^a-z0-9\-\.]', '', seo_name.replace(" ", "-"))
    
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    if not seo_name.startswith(today_str):
        seo_name = f"{today_str}-{seo_name}"
        
    target_path = os.path.join(posts_dir, seo_name)
    
    with open(next_draft, "r", encoding="utf-8") as f:
        md_content = f.read()
        
    # Automaticke prirazeni obrazku podle obsahu clanku pro luxusni vzhled
    image_url = "https://unsplash.com" # default
    if "aos" in filename.lower() or "trading" in md_content.lower():
        image_url = "https://unsplash.com" # trading/charts
    elif "vps" in md_content.lower() or "server" in md_content.lower():
        image_url = "https://unsplash.com" # server/tech
        
    # Konverze zakladniho markdownu do cisteho HTML
    html_content = md_content
    html_content = re.sub(r'^# (.*)', r'<h1>\1</h1>', html_content, flags=re.M)
    html_content = re.sub(r'^## (.*)', r'<h2>\1</h2>', html_content, flags=re.M)
    html_content = re.sub(r'^### (.*)', r'<h3>\1</h3>', html_content, flags=re.M)
    html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
    
    # Odkazy na affiliate nastroje v novem okne
    html_content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank" class="affiliate-link">\1</a>', html_content)

    # Zabaleni do premioveho minimalistickeho designu RoamGenius
    full_html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RoamGenius Hub</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <header class="main-header">
        <div class="logo"><a href="../index.html">RoamGenius</a></div>
        <p class="subtitle">AUTOMATED TRADING & GEOGRAPHIC ARBITRAGE</p>
    </header>
    <main class="container">
        <article class="single-post">
            <img src="{image_url}" class="featured-image" alt="Featured Image">
            <div class="article-body">
                {html_content}
            </div>
        </article>
    </main>
    <footer>
        <p>&copy; {datetime.utcnow().year} RoamGenius. Vsechna prava vyhrazena.</p>
    </footer>
</body>
</html>"""

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    os.remove(next_draft)
    print(f"Uspesne publikovano s krasnou URL: {seo_name}")
    
    generate_index_and_rss()

def generate_index_and_rss():
    post_files = sorted(glob.glob("posts/*.html"), reverse=True)
    posts_list_html = ""
    rss_items = ""
    
    for pf in post_files:
        filename = os.path.basename(pf)
        date_part = filename[:10]
        # Vyčištění názvu pro hezké zobrazení v seznamu
        title_part = filename[11:-5].replace("-", " ").title()
        
        posts_list_html += f"""
        <article class="post-card">
            <span class="date">{date_part}</span>
            <h2><a href="posts/{filename}">{title_part}</a></h2>
            <p>Klikněte pro otevření kompletní hloubkové analýzy a nastavení systémů...</p>
            <a href="posts/{filename}" class="read-more">Číst analýzu &rarr;</a>
        </article>
        """
        
        rss_items += f"""
        <item>
            <title>{title_part}</title>
            <link>https://roamgenius.com{filename}</link>
            <guid>https://roamgenius.com{filename}</guid>
            <pubDate>{date_part}T09:00:00Z</pubDate>
            <description>Nová expertní analýza na RoamGenius Hub</description>
        </item>
        """
        
    # Hlavni stranka s logem identickym jako vas blog
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RoamGenius Hub</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="main-header">
        <div class="logo"><a href="index.html">RoamGenius</a></div>
        <p class="subtitle">AUTOMATED TRADING & GEOGRAPHIC ARBITRAGE</p>
    </header>
    <main class="container">
        <section class="posts-grid">
            {posts_list_html}
        </section>
    </main>
    <footer>
        <p>&copy; {datetime.utcnow().year} RoamGenius. Vsechna prava vyhrazena.</p>
    </footer>
</body>
</html>""")

    with open("rss.xml", "w", encoding="utf-8") as f:
        f.write(f"<?xml version='1.0' encoding='UTF-8' ?><rss version='2.0'><channel><title>RoamGenius Hub</title><link>https://hub.roamgenius.com</link><description>Trading & Cestování</description>{rss_items}</channel></rss>")

if __name__ == "__main__":
    main()
