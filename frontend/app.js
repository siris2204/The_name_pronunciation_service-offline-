const listEl = document.getElementById('list');
const searchEl = document.getElementById('search');
const addForm = document.getElementById('add-form');
const newNameEl = document.getElementById('new-name');

async function fetchJSON(url, opts) {
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function rowTemplate(item) {
  const hasAudio = !!item.audio_path;
  return `
    <div class="row" data-id="${item.id}">
      <div class="name">${item.name}</div>
      <button class="play" ${hasAudio ? "" : "disabled"}>Play</button>
      <button class="edit">Edit</button>
      <button class="regen">Mark Regen</button>
      <button class="danger delete">Delete</button>
    </div>
  `;
}

async function loadAll() {
  const data = await fetchJSON('/api/names');
  renderList(data);
}

async function search(q) {
  if (!q) return loadAll();
  const data = await fetchJSON('/api/names/search?q=' + encodeURIComponent(q));
  renderList(data);
}

function renderList(items) {
  if (!items.length) {
    listEl.innerHTML = '<div class="empty">No names found</div>';
    return;
  }
  listEl.innerHTML = items.map(rowTemplate).join('');
}

listEl.addEventListener('click', async (e) => {
  const row = e.target.closest('.row');
  if (!row) return;
  const id = row.dataset.id;

  if (e.target.classList.contains('play')) {
    const audio = new Audio('/api/audio/' + id);
    audio.play().catch(console.error);
  }

  if (e.target.classList.contains('edit')) {
    const current = row.querySelector('.name').textContent;
    const next = prompt('Update name:', current);
    if (next && next.trim() && next !== current) {
      await fetchJSON('/api/names/' + id, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name: next.trim() })
      });
      await loadAll();
      alert('Updated. Run the audio generator script to refresh MP3.');
    }
  }

  if (e.target.classList.contains('regen')) {
    const current = row.querySelector('.name').textContent;
    await fetchJSON('/api/names/' + id, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ name: current })
    });
    await loadAll();
    alert('Marked for regeneration. Run the audio generator script.');
  }

  if (e.target.classList.contains('delete')) {
    if (confirm('Delete this name?')) {
      await fetch('/api/names/' + id, { method: 'DELETE' });
      await loadAll();
    }
  }
});

searchEl.addEventListener('input', (e) => {
  search(e.target.value.trim());
});

addForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const val = newNameEl.value.trim();
  if (!val) return;
  await fetchJSON('/api/names', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ name: val })
  });
  newNameEl.value = '';
  await loadAll();
  alert('Added. Run the audio generator script to create audio.');
});

loadAll().catch(console.error);
