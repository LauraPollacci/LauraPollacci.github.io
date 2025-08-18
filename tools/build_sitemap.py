#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, subprocess, datetime, pathlib

BASE_URL = os.getenv("BASE_URL", "https://laurapollacci.github.io").rstrip("/")
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "sitemap.xml"

EXCLUDE_DIRS = {".git", ".github", "assets", "tools", "node_modules", "_site"}
INCLUDE_EXT = {".html"}

def is_excluded(p: pathlib.Path) -> bool:
    parts = set(p.parts)
    return any(d in parts for d in EXCLUDE_DIRS)

def lastmod_iso(p: pathlib.Path) -> str:
    try:
        dt = subprocess.check_output(
            ["git", "log", "-1", "--format=%cI", "--", str(p)],
            cwd=str(ROOT), text=True
        ).strip()
        if dt:
            return dt
    except Exception:
        pass
    ts = p.stat().st_mtime
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ")

def file_to_url(p: pathlib.Path) -> str:
    rel = p.relative_to(ROOT).as_posix()
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return f"{BASE_URL}/{rel}".replace("//", "/") if rel else f"{BASE_URL}/"

def collect_pages():
    for p in ROOT.rglob("*.html"):
        if is_excluded(p):
            continue
        yield p

def build():
    urls = []
    for p in collect_pages():
        urls.append((file_to_url(p), lastmod_iso(p)))
    urls.sort(key=lambda x: x[0])

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for loc, lm in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{lm}</lastmod>")
        lines.append("    <changefreq>monthly</changefreq>")
        lines.append("  </url>")
    lines.append("</urlset>\n")

    new = "\n".join(lines)
    old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if new != old:
        OUT.write_text(new, encoding="utf-8")
        print(f"Wrote {OUT.name} ({len(urls)} urls)")
    else:
        print("No changes to sitemap.")

if __name__ == "__main__":
    sys.exit(build() or 0)
