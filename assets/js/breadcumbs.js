(function () {
  // === Basepath: user site => "/"
  const base = "/";

  // === Mini mappa: solo i padri che vuoi vedere (etichette "umane")
  const siteMap = {
  "/":               { title: "Home" },
  "/publications/":  { title: "Publications", parent: "/" },
  "/teaching/":      { title: "Teaching",     parent: "/" },
  "/research/":      { title: "Research",     parent: "/" },
  "/about/":         { title: "About",        parent: "/" },
  "/txa/":           { title: "TXA",          parent: "/" }
};
  // === Utils
  function normalizePath(p) {
  let out = p.replace(/[?#].*$/, "");              // togli query/hash

  // /index.html -> /
  out = out.replace(/\/index\.html?$/i, "/");

  // se non è la home, togli estensione .html/.htm (es. /research.html -> /research)
  if (out !== "/") out = out.replace(/\.html?$/i, "");

  if (out === "" || out === "/") return "/";       // home
  if (!out.endsWith("/")) out += "/";              // assicurati dello slash finale
  if (!out.startsWith("/")) out = "/" + out;       // e dello slash iniziale
  return out;
}
  function cleanTitle(t) {
    t = t || "";
    // rimuovi prefisso "LP | " o "LP - "
    t = t.replace(/^\s*LP\s*[\|\-–]\s*/i, "");
    // se restano separatori, prendi la prima parte
    t = t.split(/\s+[|\-–]\s+/)[0];
    return t.trim();
  }
  function currentPageTitle() {
  // 1) prova prima il titolo dichiarato sull'header
  const headerWithTitle =
    document.querySelector('#main header[title], .inner header[title], header.main[title], header.major[title], header[title]');
  if (headerWithTitle) {
    const t = headerWithTitle.getAttribute('title');
    if (t && t.trim()) return t.trim();
  }

//   // 2) fallback: H1 della pagina
//   const h1 = document.querySelector('#main h1, .inner h1, header.main h1, h1');
//   if (h1 && h1.textContent.trim()) return h1.textContent.trim();

  // 3) fallback finale: <title> ripulito (toglie il prefisso “LP | ”)
  return cleanTitle(document.title || "");
}
  function hostJoin(path) { return path; } // user site: nessun basepath da aggiungere

  const el = document.getElementById("breadcrumbs");
  if (!el) return;

  const current = normalizePath(location.pathname);

  // (Opzionale per-pagina) consenti di dichiarare il parent via meta:
  // <meta name="breadcrumb-parent" content="/teaching/">
  const metaParent = (document.querySelector('meta[name="breadcrumb-parent"]')?.content || "").trim();
  const pageNode = siteMap[current] || {};
  if (!pageNode.parent && metaParent) {
    pageNode.parent = normalizePath(metaParent);
  }

  // Home: mostra solo "Home"
  if (current === "/") {
    el.innerHTML = '<ol><li aria-current="page">' + (siteMap["/"]?.title || "Home") + '</li></ol>';
    return;
  }

  // Costruisci catena: usa parent dichiarati (mappa o meta). Se manca, salta a Home.
  const chainPaths = [];
  chainPaths.push(current);

  let cur = current;
  while (true) {
    const node = (cur === current) ? pageNode : siteMap[cur];
    if (node && node.parent) {
      cur = normalizePath(node.parent);
      chainPaths.push(cur);
      if (cur === "/") break;
    } else {
      if (cur !== "/") chainPaths.push("/");
      break;
    }
  }
  chainPaths.reverse();

  function titleFor(path) {
    if (siteMap[path] && siteMap[path].title) return siteMap[path].title;
    if (path === "/") return "Home";
    if (path === current) return currentPageTitle();
    // parent non mappati non dovrebbero comparire; fallback:
    return "";
  }

  // Render
  const ol = document.createElement("ol");
  chainPaths.forEach((p, i) => {
    const li = document.createElement("li");
    const last = i === chainPaths.length - 1;
    const t = titleFor(p) || p;
    if (last) {
      li.textContent = t;
      li.setAttribute("aria-current", "page");
    } else {
      const a = document.createElement("a");
      a.href = hostJoin(p);
      a.textContent = t;
      li.appendChild(a);
    }
    ol.appendChild(li);
  });
  el.innerHTML = "";
  el.appendChild(ol);

  // JSON-LD (facoltativo)
  try {
    const items = chainPaths.map((p, i) => ({
      "@type": "ListItem",
      "position": i + 1,
      "name": titleFor(p),
      ...(i < chainPaths.length - 1 ? { "item": location.origin + hostJoin(p) } : {})
    }));
    const ld = { "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items };
    const s = document.createElement("script");
    s.type = "application/ld+json";
    s.text = JSON.stringify(ld);
    document.head.appendChild(s);
  } catch (e) {}
})();