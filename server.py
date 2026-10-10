import os
import glob
import markdown
from flask import Flask, render_template_string, abort

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }}</title>
<style>
  :root { --bg:#fff; --fg:#24292f; --muted:#656d76; --border:#d0d7de; --link:#0969da; --code-bg:#f6f8fa; }
  * { box-sizing: border-box; }
  body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
         color:var(--fg); background:var(--bg); line-height:1.6; }
  nav { position:sticky; top:0; z-index:10; background:var(--code-bg); border-bottom:1px solid var(--border);
        padding:.6rem 1.2rem; display:flex; flex-wrap:wrap; gap:.4rem; align-items:center; }
  nav a { color:var(--link); text-decoration:none; padding:.25rem .55rem; border-radius:6px; font-size:.9rem; }
  nav a:hover { background:#ddf4ff; }
  nav .brand { font-weight:700; font-size:1rem; margin-right:.5rem; }
  main { max-width:900px; margin:0 auto; padding:2rem 1.2rem 4rem; }
  h1,h2,h3,h4 { margin-top:1.8em; margin-bottom:.6em; line-height:1.25; }
  h1 { font-size:1.9em; border-bottom:1px solid var(--border); padding-bottom:.3em; }
  h2 { font-size:1.5em; border-bottom:1px solid var(--border); padding-bottom:.3em; }
  h3 { font-size:1.25em; }
  a { color:var(--link); }
  table { border-collapse:collapse; width:100%; margin:1em 0; display:block; overflow-x:auto; }
  th,td { border:1px solid var(--border); padding:.5em .8em; text-align:left; }
  th { background:var(--code-bg); font-weight:600; }
  tr:nth-child(even) { background:var(--code-bg); }
  img { max-width:100%; height:auto; }
  code { background:var(--code-bg); padding:.15em .35em; border-radius:4px; font-size:.9em; }
  pre { background:var(--code-bg); padding:1em; border-radius:8px; overflow-x:auto; }
  pre code { background:none; padding:0; }
  blockquote { border-left:4px solid var(--border); margin:1em 0; padding:.5em 1em; color:var(--muted); }
  hr { border:none; border-top:1px solid var(--border); margin:2em 0; }
  p { margin:.6em 0; }
  ul,ol { padding-left:1.5em; }
  li { margin:.3em 0; }
  .footer { text-align:center; color:var(--muted); font-size:.85rem; margin-top:3rem; padding-top:1rem; border-top:1px solid var(--border); }
</style>
</head>
<body>
<nav>
  <span class="brand">📚 GitHubDaily</span>
  {% for item in nav %}
    <a href="/{{ item.url }}">{{ item.label }}</a>
  {% endfor %}
</nav>
<main>
{{ content_html | safe }}
</main>
<div class="footer">GitHubDaily — 开源项目精选 · 渲染自本地 Markdown 文件</div>
</body>
</html>
"""

def get_nav_items():
    """Build navigation from root-level markdown files."""
    items = []
    # README first
    readme = os.path.join(BASE_DIR, "README.md")
    if os.path.isfile(readme):
        items.append({"url": "README", "label": "首页"})
    # Year files in descending order
    year_files = sorted(glob.glob(os.path.join(BASE_DIR, "20??.md")), reverse=True)
    for f in year_files:
        name = os.path.basename(f).replace(".md", "")
        items.append({"url": name, "label": name})
    # Articles
    articles_dir = os.path.join(BASE_DIR, "articles")
    if os.path.isdir(articles_dir):
        items.append({"url": "articles", "label": "文章"})
    return items

def render_md(filepath, title):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    html = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"],
    )
    return render_template_string(TEMPLATE, title=title, content_html=html, nav=get_nav_items())

@app.route("/")
def index():
    readme = os.path.join(BASE_DIR, "README.md")
    if os.path.isfile(readme):
        return render_md(readme, "GitHubDaily")
    return "<h1>No README.md found</h1>", 404

@app.route("/articles")
def articles_list():
    articles_dir = os.path.join(BASE_DIR, "articles")
    if not os.path.isdir(articles_dir):
        abort(404)
    files = sorted(glob.glob(os.path.join(articles_dir, "*.md")))
    links = "".join(
        f'<li><a href="/articles/{i}">{os.path.basename(f).replace(".md","")}</a></li>'
        for i, f in enumerate(files)
    )
    html = f"<h1>文章</h1><ul>{links}</ul>"
    return render_template_string(TEMPLATE, title="文章", content_html=html, nav=get_nav_items())

@app.route("/articles/<int:idx>")
def article_view(idx):
    articles_dir = os.path.join(BASE_DIR, "articles")
    files = sorted(glob.glob(os.path.join(articles_dir, "*.md")))
    if idx < 0 or idx >= len(files):
        abort(404)
    return render_md(files[idx], os.path.basename(files[idx]).replace(".md", ""))

@app.route("/<string:name>")
def year_page(name):
    filepath = os.path.join(BASE_DIR, f"{name}.md")
    if not os.path.isfile(filepath):
        abort(404)
    return render_md(filepath, name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
