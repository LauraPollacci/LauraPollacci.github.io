(async function () {
  const listEl = document.getElementById('thesesList');
  const statusEl = document.getElementById('status');
  const lastUpdatedEl = document.getElementById('lastUpdated');
  const btn = document.getElementById('refreshBtn');

  async function loadData({ bustCache = false } = {}) {
    try {
      statusEl.textContent = 'Caricamento in corso…';
      const url = '/data/theses.json' + (bustCache ? `?t=${Date.now()}` : '');
      const res = await fetch(url, { cache: 'no-store' });
      if (!res.ok) throw new Error('Errore di rete ' + res.status);
      const data = await res.json();
      render(data);
      statusEl.textContent = `Trovate ${data.count ?? data.items?.length ?? 0} tesi.`;
    } catch (e) {
      statusEl.textContent = 'Impossibile caricare i dati. Riprova.';
      console.error(e);
    }
  }

  function render(data) {
    listEl.innerHTML = '';
    lastUpdatedEl.textContent = data.updated_at ? `Ultimo aggiornamento: ${new Date(data.updated_at).toLocaleString()}` : '';
    const items = Array.isArray(data.items) ? data.items : [];
    items.forEach(item => {
      const li = document.createElement('li');
      li.className = 'thesis-item';
      const title = item.title || '(titolo non disponibile)';
      const a = document.createElement('a');
      a.href = item.url || '#';
      a.target = '_blank';
      a.rel = 'noopener';
      a.textContent = title;
      const meta = document.createElement('div');
      meta.className = 'thesis-meta';
      const bits = [];
      if (item.author) bits.push(`Autore: ${item.author}`);
      if (item.degree) bits.push(`Corso: ${item.degree}`);
      if (item.year_or_date) bits.push(`Anno/Data: ${item.year_or_date}`);
      meta.textContent = bits.join(' • ');
      li.appendChild(a);
      if (bits.length) li.appendChild(meta);
      listEl.appendChild(li);
    });
  }

  btn.addEventListener('click', () => loadData({ bustCache: true }));
  loadData(); // iniziale
})();