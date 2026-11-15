"""Builds TechVestVentures Longevity Health Graphs from the monthly PNG + index.csv folder.

Default source: /workspace/longevity-supplements/graphs-for-risk-watcher/
Override with LONGEVITY_GRAPHS=/path/to/folder python3 build.py
Each category in the CSV becomes one tab. Source URLs in index.csv are
separated by ' | ' and must be https:// links.

Run from this directory:
    python3 build.py
Then commit the generated index.html, assets/style.css, .nojekyll, and issues/.
"""
import os, sys, csv, re, shutil
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, "/workspace/risk-watcher/graphs-site")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import common
from common import *

T = "TechVestVentures Longevity Health Graphs"
SRC = Path(os.environ.get(
    "LONGEVITY_GRAPHS",
    "/workspace/longevity-supplements/graphs-for-risk-watcher",
))
DECK = "https://docs.google.com/presentation/d/1luWb64cNdOh-oY6yIQwZWTZ6tVYXsN3X/edit"
NOTICE = "Not medical advice; published by the Longevity Strategies Project"
# Stable category order; extra categories in a later monthly drop append after these.
CAT_ORDER = ["Mitochondria", "Colds and Flu", "Hair", "Throat Infections"]
CAT_KEYS = {
    "Mitochondria": "mitochondria",
    "Colds and Flu": "colds-flu",
    "Hair": "hair",
    "Throat Infections": "throat-infections",
}

common.CSS += """
/* 2026-11-15 (Michael): graphs full width, no side-by-side thumbnails; sources small, directly below; click = lightbox */
main{max-width:1500px}
figure.g{display:block;margin:0 0 34px;padding:0}
figure.g a.zoom{display:block;cursor:zoom-in}
figure.g img{display:block;width:100%;max-width:none;height:auto;margin:0}
figure.g figcaption{font-size:14px;line-height:1.4;margin:6px 2px 0}figure.g figcaption p{margin:0}
figure.g figcaption .t{font-weight:700;display:inline;margin-right:6px}
figure.g figcaption .slide{display:inline}
figure.g figcaption .srcs{display:block;font-size:12px;line-height:1.35;margin-top:3px;overflow-wrap:anywhere}
figure.g figcaption .srcs a{margin-right:8px}
.notice{border-left:4px solid #8B0000;background:#faf3f3;padding:10px 14px;margin:0 0 24px;font-size:17px;line-height:1.5}
header .notice{margin:8px 0 0;font-size:15px;max-width:52rem}
#lb{position:fixed;inset:0;z-index:100;background:rgba(0,0,0,.92);display:none;align-items:center;justify-content:center;padding:12px;cursor:zoom-out}
#lb.on{display:flex}#lb img{max-width:100%;max-height:100%;object-fit:contain;background:#fff}
#lb .hint{position:absolute;top:8px;right:14px;color:#fff;font:13px Arial,sans-serif}
"""
LIGHTBOX = (
    '<div id="lb" role="dialog" aria-label="Enlarged graph"><img alt=""><span class="hint">Click or press Esc to close</span></div>'
    "<script>(function(){var lb=document.getElementById('lb'),im=lb.querySelector('img');"
    "function close(){lb.classList.remove('on');im.removeAttribute('src')}"
    "document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a.zoom');"
    "if(a){e.preventDefault();im.src=a.href;im.alt=a.getAttribute('data-alt')||'';lb.classList.add('on');return}"
    "if(lb.classList.contains('on'))close()});"
    "document.addEventListener('keydown',function(e){if(e.key==='Escape')close()})})()</script>"
)


def slug(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"^Longevity Health Graphs\s+", "", stem)
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower()
    return stem + ".webp"


def urls_of(row) -> list[str]:
    out = []
    for u in row["source_urls"].split(" | "):
        u = u.strip()
        if u and u not in out:
            if not u.startswith("https://"):
                raise SystemExit(f"Non-https source in {row['filename']}: {u}")
            out.append(u)
    return out


def load_rows():
    index = SRC / "index.csv"
    if not index.is_file():
        raise SystemExit(f"Missing index.csv in {SRC}")
    rows = list(csv.DictReader(index.open()))
    if not rows:
        raise SystemExit(f"index.csv in {SRC} has no rows")
    needed = {"filename", "category", "title", "guide_slide", "source_urls"}
    missing = needed - set(rows[0].keys())
    if missing:
        raise SystemExit(f"index.csv missing columns: {sorted(missing)}")
    for r in rows:
        p = SRC / r["filename"]
        if not p.is_file():
            raise SystemExit(f"PNG listed in index.csv not found: {p}")
        r["urls"] = urls_of(r)
        r["webp"] = slug(r["filename"])
    return rows


NOTICE_HTML = (
    f'<div class="notice"><strong>{E(NOTICE)}</strong> '
    f'These charts summarize items discussed in the '
    f'<a href="{E(DECK)}">Longevity Health Supplements Guide</a> '
    f"(Google Slides). They are not a recommendation to use or avoid any product.</div>"
)


def fig(row):
    links = " ".join(f'<a href="{E(u)}">{E(u)}</a>' for u in row["urls"])
    slide = row["guide_slide"].strip()
    alt = row["category"] + ": " + row["title"]
    cap = (
        f'<span class="t">{E(row["title"])}</span>'
        f'<span class="slide">From the Longevity Health Supplements Guide, slide {E(slide)}.</span>'
        f'<span class="srcs">Sources: {links}</span>'
    )
    return (
        f'<figure class="g" id="{E(Path(row["webp"]).stem)}">'
        f'<a class="zoom" href="img/{E(row["webp"])}" data-alt="{E(alt)}" title="Click to enlarge">'
        f'<img src="img/{E(row["webp"])}" alt="{E(alt)}" loading="lazy" width="1600" height="901"></a>'
        f"<figcaption>{cap}</figcaption></figure>"
    )


def main():
    rows = load_rows()
    by_cat = OrderedDict()
    for name in CAT_ORDER:
        by_cat[name] = []
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)
    # Drop empty reserved categories (should not happen on the current drop).
    by_cat = OrderedDict((k, v) for k, v in by_cat.items() if v)

    shutil.rmtree("issues", ignore_errors=True)
    os.makedirs("issues/img")
    os.makedirs("assets", exist_ok=True)
    if not Path("assets/logo.png").is_file():
        shutil.copy("/workspace/risk-watcher/site/assets/logo.png", "assets/logo.png")

    tabs = []
    counts = {}

    def w(k, lab, body):
        open(f"issues/{k}.html", "w").write(page(T, k, body))
        tabs.append((k, lab))

    src = OrderedDict()
    for cat, cs in by_cat.items():
        key = CAT_KEYS.get(cat, re.sub(r"[^a-z0-9]+", "-", cat.lower()).strip("-"))
        counts[cat] = len(cs)
        for r in cs:
            save_img(str(SRC / r["filename"]), f"issues/img/{r['webp']}")
            for u in r["urls"]:
                src.setdefault(u, f"{r['category']}: {r['title']}")
        body = f'<h2 class="desk">{E(cat)}</h2>{NOTICE_HTML}' + "\n".join(fig(r) for r in cs)
        w(key, cat, body)

    w(
        "sources",
        "Sources",
        f'<h2 class="desk">Sources ({len(src)} links)</h2>{NOTICE_HTML}'
        "<p>Source links as listed with each graph in the Longevity Health Graphs index. "
        f'See also the <a href="{E(DECK)}">Longevity Health Supplements Guide</a>.</p>'
        '<ul class="src">'
        + "".join(f"<li>{E(l)}: <a href=\"{E(u)}\">{E(u)}</a></li>" for u, l in src.items())
        + "</ul>",
    )

    index(T, tabs, "Sections", cur="longevity")
    html = Path("index.html").read_text()
    needle = f"<h1>{T}</h1></header>"
    insert = (
        f"<h1>{T}</h1>"
        f'<p class="notice">{E(NOTICE)}. '
        f'<a href="{E(DECK)}">Source deck</a>.</p></header>'
    )
    if needle not in html:
        raise SystemExit("Could not insert header notice into index.html")
    Path("index.html").write_text(html.replace(needle, insert, 1).replace("</body>", LIGHTBOX + "</body>", 1))
    print(counts, f"{sum(counts.values())} charts", f"{len(src)} sources")


if __name__ == "__main__":
    main()
