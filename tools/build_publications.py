#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, html, re, pathlib
from collections import defaultdict

HIGHLIGHT_AUTHOR = os.environ.get("HIGHLIGHT_AUTHOR", "Laura Pollacci")
# ===== Config =====
BIB_PATH = os.environ.get("BIB_PATH", "publications.bib")
OUT_PATH = os.environ.get("OUT_PATH", "publications.html")
TITLE    = os.environ.get("PAGE_TITLE", "Publications")
TEMPLATE_PATH = os.environ.get("TEMPLATE_PATH", "publications_template.html")

# ===== Dipendenze minime (bibtexparser) =====
try:
    import bibtexparser
except ImportError:
    print("Missing dependency: bibtexparser", file=sys.stderr)
    sys.exit(2)

def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def de_latex(s: str) -> str:
    """Sostituzioni minime da LaTeX -> testo semplice."""
    if not s:
        return ""
    # replace esatto richiesto
    s = s.replace(r'{\^\i}', 'i')
    return s

def split_authors(author_field: str):
    # BibTeX: autori separati da ' and '
    parts = [a.strip() for a in re.split(r"\s+and\s+", author_field, flags=re.I) if a.strip()]
    norm = []
    for p in parts:
        p = de_latex(p)
        # "Last, First" -> "First Last"
        if "," in p:
            last, first = [x.strip() for x in p.split(",", 1)]
            norm.append(f"{first} {last}".strip())
        else:
            norm.append(p)
    return norm

def fmt_authors(authors):
    out = []
    for a in authors:
        a_clean = de_latex(a)
        a_clean = html.escape(a_clean)
        # evidenzia il tuo nome
        if HIGHLIGHT_AUTHOR and HIGHLIGHT_AUTHOR.lower() in a.lower():
            out.append(f"<strong>{a_clean}</strong>")
        else:
            out.append(a_clean)
    # Oxford comma style
    if len(out) <= 2:
        return " and ".join(out)
    return ", ".join(out[:-1]) + ", and " + out[-1]

def pick(entr, *keys):
    for k in keys:
        if k in entr and entr[k]:
            return normalize_space(str(entr[k]))
    return ""

def entry_to_html(e):
    # campi tipici
    year = pick(e, "year")
    title = de_latex(pick(e, "title"))
    journal = de_latex(pick(e, "journal", "booktitle"))
    authors = split_authors(pick(e, "author")) if "author" in e else []
    doi = pick(e, "doi")
    url = pick(e, "url")
    pdf = pick(e, "pdf")

    parts = []
    if authors:
        parts.append(f'<span class="pub-authors">{fmt_authors(authors)}</span>')
    if year:
        parts.append(f' (<span class="pub-year">{html.escape(year)}</span>)')
    if title:
        parts.append(f' <span class="pub-title">“{html.escape(title)}”</span>.')
    if journal:
        parts.append(f' <span class="pub-venue"><em>{html.escape(journal)}</em></span>.')

    links = []
    if doi:
        doi_url = f"https://doi.org/{doi}" if not doi.lower().startswith(("http://","https://")) else doi
        links.append(f'<a href="{html.escape(doi_url)}" target="_blank" rel="noopener">DOI</a>')
    if url:
        links.append(f'<a href="{html.escape(url)}" target="_blank" rel="noopener">Link</a>')
    if pdf:
        links.append(f'<a href="{html.escape(pdf)}" target="_blank" rel="noopener">PDF</a>')
    if links:
        parts.append(' <span class="pub-links">[' + " · ".join(links) + ']</span>')

    return "<li>" + "".join(parts) + "</li>"

def render_page(grouped, years_sorted):
    # Se esiste un template, usa {{TITLE}} e {{LIST}}
    content = []
    for y in years_sorted:
        content.append(f'<h3>{html.escape(str(y))}</h3>')
        content.append('<ul class="pub-list" reversed>')
        for e in grouped[y]:
            content.append(entry_to_html(e))
        content.append('</ul>')

    generated_list = "\n".join(content)

    if pathlib.Path(TEMPLATE_PATH).exists():
        tpl = pathlib.Path(TEMPLATE_PATH).read_text(encoding="utf-8")
        return tpl.replace("{{TITLE}}", html.escape(TITLE)).replace("{{LIST}}", generated_list)

    # Fallback: pagina minimale standalone (senza template)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TITLE)}</title>
<style>
body{{font:16px/1.6 system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:2rem;}}
h1,h2,h3{{line-height:1.25;margin:1.2rem 0 .6rem}}
.pub-list{{margin:0 0 1.5rem 1.2rem;}}
.pub-list li{{margin:.3rem 0}}
.pub-authors strong{{font-weight:700}}
.pub-title{{font-weight:600}}
.pub-links a{{text-decoration:none;border-bottom:1px solid;}}
header a{{text-decoration:none;border-bottom:1px solid;}}
</style>
</head>
<body>
<header><h1>{html.escape(TITLE)}</h1></header>
<main>
{generated_list}
</main>
</body>
</html>"""

def main():
    if not pathlib.Path(BIB_PATH).exists():
        print(f"BibTeX not found: {BIB_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(BIB_PATH, "r", encoding="utf-8") as f:
        db = bibtexparser.load(f)

    # ordina per anno decrescente, poi titolo
    entries = db.entries or []
    for e in entries:
        # normalizza chiavi a lower (bibtexparser già lo fa ma be safe)
        for k in list(e.keys()):
            e[k.lower()] = e.pop(k)

    def year_key(e):
        try:
            return int(e.get("year", 0))
        except Exception:
            return 0

    entries.sort(key=lambda e: (year_key(e), e.get("title","").lower()), reverse=True)

    # group by year
    grouped = defaultdict(list)
    for e in entries:
        y = e.get("year", "n.d.")
        grouped[y].append(e)

    years_sorted = sorted(grouped.keys(), key=lambda y: int(y) if str(y).isdigit() else -1, reverse=True)

    out_html = render_page(grouped, years_sorted)

    out_file = pathlib.Path(OUT_PATH)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    old = out_file.read_text(encoding="utf-8") if out_file.exists() else ""
    if old != out_html:
        out_file.write_text(out_html, encoding="utf-8")
        print(f"Wrote {OUT_PATH}")
    else:
        print("No changes in publications.")

if __name__ == "__main__":
    main()
