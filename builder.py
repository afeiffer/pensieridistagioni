import os
import shutil
import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# Configurazione cartelle
CONTENT_DIR = "content"
TEMPLATES_DIR = "templates"
STATIC_DIR = "static"
OUTPUT_DIR = "public"

def get_season_theme(date_val):
    if isinstance(date_val, str):
        date_obj = datetime.strptime(date_val, "%Y-%m-%d")
    elif isinstance(date_val, datetime):
        date_obj = date_val
    else:
        date_obj = datetime.combine(date_val, datetime.min.time())

    month = date_obj.month

    # Primavera (Marzo - Maggio): Toni salvia, verde bosco fresco e terra chiara
    if 3 <= month <= 5:
        return {
            "name": "Primavera",
            "bg_card": "bg-emerald-50/70 hover:bg-emerald-50 border-emerald-200/80",
            "bg_page": "bg-emerald-50/40",
            "text_main": "text-emerald-950",
            "text_muted": "text-emerald-700/80",
            "title_hover": "group-hover:text-emerald-700",
            "badge": "bg-emerald-100 text-emerald-900 border-emerald-300",
            "border_accent": "border-emerald-600"
        }
    # Estate (Giugno - Agosto): Toni ambrati, caldi e solari
    elif 6 <= month <= 8:
        return {
            "name": "Estate",
            "bg_card": "bg-amber-50/70 hover:bg-amber-50 border-amber-200/80",
            "bg_page": "bg-amber-50/40",
            "text_main": "text-amber-950",
            "text_muted": "text-amber-800/80",
            "title_hover": "group-hover:text-amber-700",
            "badge": "bg-amber-100 text-amber-900 border-amber-300",
            "border_accent": "border-amber-500"
        }
    # Autunno (Settembre - Novembre): Toni ruggine, rame e terra calda
    elif 9 <= month <= 11:
        return {
            "name": "Autunno",
            "bg_card": "bg-orange-50/70 hover:bg-orange-50 border-orange-200/80",
            "bg_page": "bg-orange-50/40",
            "text_main": "text-orange-950",
            "text_muted": "text-orange-800/80",
            "title_hover": "group-hover:text-orange-700",
            "badge": "bg-orange-100 text-orange-900 border-orange-300",
            "border_accent": "border-orange-600"
        }
    # Inverno (Dicembre - Febbraio): Toni blu freddo, lavagna e ghiaccio
    else:
        return {
            "name": "Inverno",
            "bg_card": "bg-slate-100/80 hover:bg-slate-100 border-slate-300/80",
            "bg_page": "bg-slate-100/50",
            "text_main": "text-slate-950",
            "text_muted": "text-slate-600",
            "title_hover": "group-hover:text-sky-700",
            "badge": "bg-slate-200 text-slate-900 border-slate-400",
            "border_accent": "border-slate-600"
        }

def setup_output_dir():
    """Pulisce e rigenera la cartella di output."""
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    os.makedirs(os.path.join(OUTPUT_DIR, "posts"))

    # Copia i file statici se esistono
    if os.path.exists(STATIC_DIR):
        shutil.copytree(STATIC_DIR, os.path.join(OUTPUT_DIR, "static"))


def build_blog():
    setup_output_dir()

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    index_template = env.get_template("index.html")
    post_template = env.get_template("post.html")
    page_template = env.get_template("page.html")

    posts = []

    # 1. Processa i post (content/posts/)
    posts_dir = os.path.join(CONTENT_DIR, "posts")
    if os.path.exists(posts_dir):
        for filename in os.listdir(posts_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(posts_dir, filename)
                post_data = frontmatter.load(filepath)

                html_content = markdown.markdown(
                    post_data.content,
                    extensions=['fenced_code', 'tables']
                )

                post_metadata = post_data.metadata
                post_metadata['content'] = html_content
                post_metadata['season'] = get_season_theme(post_metadata['date'])
                posts.append(post_metadata)

                # Genera HTML del singolo post
                rendered_post = post_template.render(
                    title=post_metadata['title'],
                    date=post_metadata['date'],
                    content=html_content,
                    season=post_metadata['season']
                )

                out_post_path = os.path.join(OUTPUT_DIR, "posts", f"{post_metadata['slug']}.html")
                with open(out_post_path, "w", encoding="utf-8") as f:
                    f.write(rendered_post)

    # Ordina i post per data
    posts.sort(key=lambda x: str(x.get('date', '')), reverse=True)

    # 2. Processa le pagine fisse (content/pages/)
    pages_dir = os.path.join(CONTENT_DIR, "pages")
    if os.path.exists(pages_dir):
        for filename in os.listdir(pages_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(pages_dir, filename)
                page_data = frontmatter.load(filepath)

                html_content = markdown.markdown(
                    page_data.content,
                    extensions=['fenced_code', 'tables']
                )

                page_metadata = page_data.metadata

                rendered_page = page_page = page_template.render(
                    title=page_metadata['title'],
                    content=html_content
                )

                out_page_path = os.path.join(OUTPUT_DIR, f"{page_metadata['slug']}.html")
                with open(out_page_path, "w", encoding="utf-8") as f:
                    f.write(rendered_page)

    # 3. Genera la homepage (index.html)
    rendered_index = index_template.render(title="Home", posts=posts)
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(rendered_index)

    print("Blog generato con successo !")


if __name__ == "__main__":
    build_blog()