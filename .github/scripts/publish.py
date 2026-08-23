import os
import glob
import re
from datetime import datetime, timezone

def clean_all_html_tags(text):
    """Kompletně vyčistí jakékoliv staré HTML tagy a zanechá pouze čistý text."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

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
    
    # Čistá SEO URL
    seo_name = filename.lower().replace(".md", ".html")
    seo_name = re.sub(r'[^a-z0-9\-\.]', '', seo_name.replace(" ", "-"))
    
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not seo_name.startswith(today_str):
        seo_name = f"{today_str}-{seo_name}"
        
    target_path = os.path.join(posts_dir, seo_name)
    
    with open(next_draft, "r", encoding="utf-8") as f:
        raw_content = f.read()
        
    # Výběr stabilních obrázků z volné sítě Pexels
    image_url = "https://pexels.com"
    if "vps" in seo_name:
        image_url = "https://pexels.com"
    elif "psychologie" in seo_name:
        image_url = "https://pexels.com"

    # Zpracování textu řádek po řádku - ochrana proti zdvojeným tagům
    lines = raw_content.split('\n')
    body_html = ""
    
    for line in lines:
        cleaned_line = clean_all_html_tags(line)
        if not cleaned_line:
            continue
            
        if line.strip().startswith('# '):
            body_html += f"<h1>{cleaned_line}</h1>\n"
        elif line.strip().startswith('## '):
            body_html += f"<h2>{cleaned_line}</h2>\n"
        elif line.strip().startswith('### '):
            body_html += f"<h3>{cleaned_line}</h3>\n"
        else:
            body_html += f"<p>{cleaned_line}</p>\n"

    # Šablona detailu článku (Upozornění: style.css i logo.png načítáme absolutně z kořene přes / )
    full_html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RoamGenius Hub</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="/index.html" class="nav-logo-link">
                <img src="/logo.png" class="brand-logo" alt="RoamGenius">
            </a>
            <span class="nav-tagline">HUB</span>
        </div>
    </nav>
    <nav class="navbar-spacer"></nav>
    <main class="container">
        <article class="single-post">
            <div class="post-meta">{datetime.now(timezone.utc).strftime("%d. %m. %Y")}</div>
            <img src="{image_url}" class="featured-image" alt="Article Image">
            <div class="article-body">
                {body_html}
            </div>
        </article>
    </main>
    <footer>
        <p>&copy; {datetime.now(timezone.utc).year} RoamGenius. Všechna práva vyhrazená.</p>
    </footer>
</body>
</html>"""

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    os.remove(next_draft)
    print(f"Uspesne publikovano: {seo_name}")
    
    generate_index_and_rss()

def generate_index_and_rss():
    post_files = sorted(glob.glob("posts/*.html"), reverse=True)
    posts_list_html = ""
    rss_items = ""
    
    for pf in post_files:
        filename = os.path.basename(pf)
        date_part = filename[:10]
        try:
            date_obj = datetime.strptime(date_part, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d. %m. %Y")
        except:
            formatted_date = date_part
            
        title_part = filename[11:-5].replace("-", " ").title()
        
        with open(pf, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Bezpečné vytažení URL obrázku z vygenerovaného článku
        img_match = re.search(r'src="(.*?)"', content)
        thumb_url = img_match.group(1) if img_match else "https://pexels.com"
        
        # Precizní extrakce čistého textu pro perex (vynechá navigaci a bere jen text z odstavců <p>)
        p_matches = re.findall(r'<p>(.*?)</p>', content)
        clean_paragraphs = [clean_all_html_tags(p) for p in p_matches if "Všechna práva vyhrazená" not in p]
        
        perex = ""
        if clean_paragraphs:
            perex = " ".join(clean_paragraphs)[:200].strip() + "..."
        else:
            perex = "Klikněte pro otevření kompletní hloubkové analýzy..."
        
        posts_list_html += f"""
        <article class="post-card">
            <div class="post-card-image">
                <img src="{thumb_url}" alt="{title_part}">
            </div>
            <div class="post-card-content">
                <span class="date">{formatted_date}</span>
                <h2><a href="posts/{filename}">{title_part}</a></h2>
                <p>{perex}</p>
                <a href="posts/{filename}" class="read-more">Číst analýzu &rarr;</a>
            </div>
        </article>
        """
        
        rss_items += f"""
        <item>
            <title>{title_part}</title>
            <link>https://roamgenius.com{filename}</link>
            <guid>https://roamgenius.com{filename}</guid>
            <pubDate>{date_part}T09:00:00Z</pubDate>
            <description>{perex}</description>
        </item>
        """
        
    # Šablona hlavní stránky (index.html)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RoamGenius Hub</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="/index.html" class="nav-logo-link">
                <img src="/logo.png" class="brand-logo" alt="RoamGenius">
            </a>
            <span class="nav-tagline">HUB</span>
        </div>
    </nav>
    <nav class="navbar-spacer"></nav>
    <main class="container">
        <section class="posts-list">
            {posts_list_html}
        </section>
    </main>
    <footer>
        <p>&copy; {datetime.now().year} RoamGenius. Všechna práva vyhrazená.</p>
    </footer>
</body>
</html>""")

    with open("rss.xml", "w", encoding="utf-8") as f:
        f.write(f"<?xml version='1.0' encoding='UTF-8' ?><rss version='2.0'><channel><title>RoamGenius Hub</title><link>https://roamgenius.com</link><description>Trading & Cestování</description>{rss_items}</channel></rss>")

if __name__ == "__main__":
    main()
