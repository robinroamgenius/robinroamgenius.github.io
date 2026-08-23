import os
import glob
import re
from datetime import datetime, timezone

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
    
    # Čistá SEO url adresa
    seo_name = filename.lower().replace(".md", ".html")
    seo_name = re.sub(r'[^a-z0-9\-\.]', '', seo_name.replace(" ", "-"))
    
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not seo_name.startswith(today_str):
        seo_name = f"{today_str}-{seo_name}"
        
    target_path = os.path.join(posts_dir, seo_name)
    
    with open(next_draft, "r", encoding="utf-8") as f:
        md_content = f.read()
        
    # Výběr 100% stabilních obrázků (Pexels)
    image_url = "https://pexels.com"
    if "vps" in seo_name or "server" in md_content.lower():
        image_url = "https://pexels.com"
    elif "psychologie" in seo_name or "boti" in seo_name:
        image_url = "https://pexels.com"
        
    # Převod základního markdownu do HTML
    html_content = md_content
    html_content = re.sub(r'^# (.*)', r'<h1>\1</h1>', html_content, flags=re.M)
    html_content = re.sub(r'^## (.*)', r'<h2>\1</h2>', html_content, flags=re.M)
    html_content = re.sub(r'^### (.*)', r'<h3>\1</h3>', html_content, flags=re.M)
    html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
    html_content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank" class="affiliate-link">\1</a>', html_content)

    paragraphs = html_content.split('\n\n')
    formatted_paragraphs = []
    for p in paragraphs:
        if not p.strip().startswith('<h') and p.strip():
            formatted_paragraphs.append(f"<p>{p.strip()}</p>")
        else:
            formatted_paragraphs.append(p.strip())
    html_content = '\n'.join(formatted_paragraphs)

    # ŠABLONA DETAILU ČLÁNKU (Logo se volá z kořene přes ../logo.png)
    full_html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RoamGenius Hub</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="../index.html" class="nav-logo-link">
                <img src="../logo.png" class="brand-logo" alt="RoamGenius">
            </a>
            <span class="nav-tagline">HUB</span>
        </div>
    </nav>
    <main class="container">
        <article class="single-post">
            <div class="post-meta">{datetime.now(timezone.utc).strftime("%d. %m. %Y")}</div>
            <img src="{image_url}" class="featured-image" alt="Featured Image">
            <div class="article-body">
                {html_content}
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
    print(f"Uspesne publikovano do posts: {seo_name}")
    
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
            
        img_match = re.search(r'src="(.*?)"', content)
        thumb_url = img_match.group(1) if img_match else "https://pexels.com"
        
        clean_text = re.sub(r'<[^>]*>', '', content)
        clean_text = clean_text.replace("RoamGenius", "").replace("HUB", "").replace("Home", "").strip()
        perex = clean_text[:220].strip() + "..."
        
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
        
    # ŠABLONA HLAVNÍ STRÁNKY (Logo se volá přímo přes logo.png)
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
    <nav class="navbar">
        <div class="nav-container">
            <a href="index.html" class="nav-logo-link">
                <img src="logo.png" class="brand-logo" alt="RoamGenius">
            </a>
            <span class="nav-tagline">HUB</span>
        </div>
    </nav>
    <main class="container">
        <section class="posts-list">
            {posts_list_html}
        </section>
    </main>
    <footer>
        <p>&copy; {datetime.now(timezone.utc).year} RoamGenius. Všechna práva vyhrazená.</p>
    </footer>
</body>
</html>""")

    with open("rss.xml", "w", encoding="utf-8") as f:
        f.write(f"<?xml version='1.0' encoding='UTF-8' ?><rss version='2.0'><channel><title>RoamGenius Hub</title><link>https://roamgenius.com</link><description>Trading & Cestování</description>{rss_items}</channel></rss>")

if __name__ == "__main__":
    main()
