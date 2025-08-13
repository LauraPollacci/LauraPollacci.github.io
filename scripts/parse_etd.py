#!/usr/bin/env python3
import json, time, re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

BASE = "https://etd.adm.unipi.it"
START_URL = f"{BASE}/ETD-db/ETD-search/search_by_advisor?advisor_name=Pollacci"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ThesisBot/1.0; +https://github.io)",
    "Accept-Language": "it,en;q=0.8",
}

session = requests.Session()
session.headers.update(HEADERS)
TIMEOUT = 20

def get_soup(url):
    r = session.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")

def iter_result_pages(start_url):
    url = start_url
    seen = set()
    while url and url not in seen:
        seen.add(url)
        soup = get_soup(url)
        yield soup, url
        # Tenta a trovare un link "Successivo" o "Next"
        next_link = soup.find("a", string=re.compile(r"(Successivo|Next)", re.I))
        if next_link and next_link.get("href"):
            url = urljoin(url, next_link["href"])
        else:
            # In alcuni temi il paging è via numeri
            current = soup.find("a", attrs={"class": re.compile(r"current|active", re.I)}) or soup.find("span", attrs={"class": re.compile(r"current|active", re.I)})
            if current:
                nxt = current.find_next("a")
                url = urljoin(url, nxt["href"]) if nxt and nxt.get("href") else None
            else:
                url = None

def parse_result_links(soup):
    """
    Estrae i link alle singole tesi dai risultati.
    Heuristica: link che contengono 'view' nell'URL della ETD.
    """
    links = []
    for a in soup.select("a[href]"):
        href = a["href"]
        if "/ETD-db/" in href and re.search(r"view|ETD-.*", href, re.I):
            full = urljoin(BASE, href)
            # Evita link duplicati e filtra solo pagine di dettaglio (heuristica)
            if "view" in full or "ETD-" in full:
                links.append(full)
    return list(dict.fromkeys(links))  # unique e preserva l'ordine

def clean_text(x):
    return re.sub(r"\s+", " ", x or "").strip()

def extract_field_by_label(soup, label_regex):
    """
    Cerca un <dt>label</dt><dd>valore</dd> oppure una riga tabellare con etichetta.
    """
    # DL
    for dt in soup.find_all("dt"):
        if re.search(label_regex, dt.get_text(" "), re.I):
            dd = dt.find_next("dd")
            if dd:
                return clean_text(dd.get_text(" "))
    # Table rows
    for tr in soup.find_all("tr"):
        th = tr.find(["th","td"])
        if th and re.search(label_regex, th.get_text(" "), re.I):
            td = th.find_next("td")
            if td:
                return clean_text(td.get_text(" "))
    return None

def parse_thesis_page(url):
    soup = get_soup(url)

    # TITOLO: prova varie strategie
    title = None
    h1 = soup.find("h1")
    if h1:
        title = clean_text(h1.get_text(" "))

    if not title:
        title = extract_field_by_label(soup, r"Titolo|Title")

    if not title and soup.title:
        # Spesso <title> contiene "Titolo - ETD"
        title = clean_text(soup.title.get_text()).split(" - ")[0]

    author = extract_field_by_label(soup, r"Autore|Author")
    degree = extract_field_by_label(soup, r"Corso di laurea|Degree|Laurea")
    year = extract_field_by_label(soup, r"Anno|Year|Data di discussione|Discussione|Date")
    abstract = extract_field_by_label(soup, r"Abstract|Riassunto")

    return {
        "title": title,
        "author": author,
        "degree": degree,
        "year_or_date": year,
        "abstract": abstract,
        "url": url,
    }

def main():
    # raccogli tutti i link tesi
    thesis_links = []
    for soup, page_url in iter_result_pages(START_URL):
        thesis_links.extend(parse_result_links(soup))
    thesis_links = list(dict.fromkeys(thesis_links))

    results = []
    for i, url in enumerate(thesis_links, 1):
        try:
            data = parse_thesis_page(url)
            results.append(data)
        except Exception as e:
            results.append({"url": url, "error": str(e)})
        time.sleep(0.4)  # piccolo rispetto per il server

    payload = {
        "advisor": "Pollacci",
        "source": START_URL,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(results),
        "items": results,
    }

    # salva in data/theses.json
    import os
    os.makedirs("data", exist_ok=True)
    with open("data/theses.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
