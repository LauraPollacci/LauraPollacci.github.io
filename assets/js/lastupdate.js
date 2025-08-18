(function () {
  function setLastUpdated() {
    var el = document.getElementById('last-updated');
    if (!el) return;

    var d = new Date(document.lastModified); // data per-**pagina**
    if (isNaN(d)) { el.textContent = '—'; return; }

    // Formato leggibile (in inglese). Se preferisci italiano, usa 'it-IT'
    var opts = { year: 'numeric', month: 'long', day: 'numeric' };
    el.textContent = new Intl.DateTimeFormat('en-US', opts).format(d);
    el.setAttribute('datetime', d.toISOString());
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setLastUpdated);
  } else {
    setLastUpdated();
  }
})();