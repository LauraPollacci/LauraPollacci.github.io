/*
	By Laura Pollacci
*/

/* Per "project site", attivare questa riga (oppure mettere data-basepath sull'<html>):
document.documentElement.dataset.basepath = "/nome-repo/";
*/

(function () {
const base = document.documentElement.dataset.basepath || "/";

// === 1) MAPPA DEL SITO ===
// Path normalizzati: sempre con / iniziale e finale ("/", "/sezione/", "/sezione/pagina/")
const siteMap = {
	"/": { title: "Home" },

	// ESEMPI:
	"/portfolio/":        { title: "Pagina principale", parent: "/" },
	"/portfolio/app-x/":  { title: "Sottopagina",       parent: "/portfolio/" },
	"/about/":            { title: "Chi sono", parent: "/" },
	"/contatti/":         { title: "Contatti", parent: "/" }
};

// === 2) COSTRUZIONE BREADCRUMB ===
const hostBase = (function () {
	// unisce basepath e path assoluto del sito
	return function join(path) {
	// path è tipo "/qualcosa/"
	if (base === "/") return path;
	return base.replace(/\/$/, "") + path; // "/repo" + "/x/" => "/repo/x/"
	};
})();

function normalizePath(pathname) {
	let p = pathname;
	if (base !== "/" && p.startsWith(base)) p = p.slice(base.length - 1);
	p = p.replace(/index\.html?$/i, "");
	if (p === "" || p === "/") return "/";
	if (!p.endsWith("/")) p += "/";
	if (!p.startsWith("/")) p = "/" + p;
	return p;
}

const el = document.getElementById("breadcrumbs");
if (!el) return;

const current = normalizePath(location.pathname);

// Se la pagina non è in siteMap, usa <title> come fallback e mette genitore Home
const startNode = siteMap[current] || { title: (document.title || ""), parent: "/" };

// Risali ai genitori finché esistono
const chain = [];
let node = startNode, cursor = current;
while (node) {
	chain.push({ path: cursor, title: node.title });
	if (!node.parent) break;
	cursor = node.parent;
	node = siteMap[cursor];
}

// Assicura che Home sia in testa
if (!chain.some(c => c.path === "/") && siteMap["/"]) {
	chain.push({ path: "/", title: siteMap["/"].title });
}
chain.reverse();

// Caso Home: mostra solo "Home"
if (current === "/") {
	el.innerHTML = '<ol><li aria-current="page">' + (siteMap["/"]?.title || "Home") + '</li></ol>';
	return;
}

// Render HTML
const ol = document.createElement("ol");
chain.forEach((c, i) => {
	const li = document.createElement("li");
	const last = i === chain.length - 1;
	if (last) {
	li.textContent = c.title;
	li.setAttribute("aria-current", "page");
	} else {
	const a = document.createElement("a");
	a.href = hostBase(c.path);
	a.textContent = c.title;
	li.appendChild(a);
	}
	ol.appendChild(li);
});
el.appendChild(ol);
})();