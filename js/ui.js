export const $ = id => document.getElementById(id);
export function message(text, error = false) {
  const box = $('message');
  box.textContent = text;
  box.className = error
    ? 'mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800'
    : 'mb-5 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800';
  box.setAttribute('role', error ? 'alert' : 'status'); box.hidden = false;
}
export function readKeys(container) {
  const keys = {};
  for (const input of $(container).querySelectorAll('[data-key]')) {
    if (!/^[A-Za-z]+$/.test(input.value)) throw new Error('Ketiga kunci wajib huruf A–Z/a–z tanpa spasi atau angka.');
    keys[input.dataset.key] = input.value;
  }
  return keys;
}
export function resetKeys(container, checkbox) {
  for (const input of $(container).querySelectorAll('[data-key]')) { input.value = ''; input.type = 'password'; }
  $(checkbox).checked = false;
}
export function setupKeyToggle(container, checkbox) {
  $(checkbox).addEventListener('change', () => {
    for (const input of $(container).querySelectorAll('[data-key]')) input.type = $(checkbox).checked ? 'text' : 'password';
  });
}
export function renderNotes(notes, {open, remove}) {
  const tbody = $('note-list'); tbody.replaceChildren();
  $('note-count').textContent = notes.length + ' catatan'; $('empty-list').hidden = notes.length > 0;
  for (const note of notes) {
    const row = document.createElement('tr'); row.className = 'border-b border-zinc-100 last:border-0';
    const code = row.insertCell(); code.className = 'px-5 py-4 font-medium'; code.textContent = note.clientCode;
    const date = row.insertCell(); date.className = 'whitespace-nowrap px-3 py-4 text-zinc-500'; date.textContent = note.sessionDate;
    const cell = row.insertCell(); cell.className = 'px-5 py-4';
    const actions = document.createElement('div'); actions.className = 'flex justify-end gap-1.5';
    for (const [label, callback] of [['Buka', open], ['Hapus', remove]]) {
      const button = document.createElement('button'); button.type = 'button'; button.className = 'secondary';
      button.textContent = label; button.addEventListener('click', () => callback(note.id)); actions.append(button);
    }
    cell.append(actions); tbody.append(row);
  }
}
export function showProcess(result, label) {
  $('process-info').textContent = label;
  const target = $('process-stages'); target.replaceChildren();
  for (const stage of result.stages) {
    const box = document.createElement('div'); box.className = 'rounded-lg border border-zinc-200 bg-zinc-50 p-3';
    const title = document.createElement('h3'); title.className = 'mb-2 text-xs font-semibold'; title.textContent = stage.title;
    const value = document.createElement('pre'); value.className = 'max-h-36 overflow-auto whitespace-pre-wrap break-words text-[11px] leading-relaxed text-zinc-600';
    value.textContent = stage.text; box.append(title, value); target.append(box);
  }
}
export function clearResult() {
  $('result-panel').hidden = true; $('result-text').textContent = ''; $('result-meta').textContent = '';
  $('process-stages').replaceChildren(); $('process-details').open = false;
  $('process-info').textContent = 'Hasil setiap tahap muncul setelah catatan dienkripsi atau dibuka.';
}
