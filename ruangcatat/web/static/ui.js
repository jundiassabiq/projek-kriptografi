export const $ = id => document.getElementById(id);
let toastTimer;
export function toast(message, error=false) {
  const box = $('toast'); box.textContent = message; box.className = error ? 'error' : '';
  box.hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(()=>box.hidden=true,6000);
}
export function action(callback) {
  return async event => {
    if (event) event.preventDefault();
    const button = event?.currentTarget;
    const wasDisabled = button?.disabled;
    if (button?.tagName === 'BUTTON') button.disabled = true;
    try { await callback(event); } catch (error) { toast(error.message, true); }
    finally { if (button?.tagName === 'BUTTON' && button.isConnected) button.disabled = wasDisabled; }
  };
}
export function keys(container) {
  const result = {};
  for (const field of $(container).querySelectorAll('[data-key]')) {
    if (!/^[A-Za-z]+$/.test(field.value)) throw new Error('Semua kunci wajib huruf A–Z/a–z, tanpa spasi atau angka.');
    result[field.dataset.key] = field.value;
  }
  return result;
}
export function setupKeyVisibility() {
  for (const box of document.querySelectorAll('[data-show-keys]')) {
    box.addEventListener('change',()=> {
      for (const field of box.closest('.key-fields').querySelectorAll('[data-key]'))
        field.type = box.checked ? 'text' : 'password';
    });
  }
}
export function download(name, content, type='application/json') {
  const url = URL.createObjectURL(new Blob([content], {type}));
  const link = document.createElement('a'); link.href=url; link.download=name;
  link.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
}
export async function fileText(input) {
  const file = input.files[0];
  if (!file) throw new Error('Pilih file terlebih dahulu.');
  if (file.size > 1024*1024) throw new Error('Maksimal ukuran file 1 MiB.');
  // Fatal decoding menolak file non-UTF-8 agar isi tidak diam-diam berubah.
  return new TextDecoder('utf-8',{fatal:true}).decode(await file.arrayBuffer());
}
export function table(container, records, callbacks) {
  const target = $(container); target.replaceChildren();
  if (!records.length) {
    const empty=document.createElement('p'); empty.className='empty';
    empty.textContent='Belum ada catatan untuk ditampilkan.'; target.append(empty); return;
  }
  const wrap=document.createElement('div'); wrap.className='table-wrap';
  const grid=document.createElement('table');
  const head=grid.createTHead().insertRow();
  for(const title of ['Klien','Tanggal sesi','Pertemuan berikutnya','Status','Tindakan']) {
    const th=document.createElement('th'); th.textContent=title; head.append(th);
  }
  const body=grid.createTBody();
  for(const row of records) {
    const tr=body.insertRow();
    for(const value of [row.code,row.session_date,row.next_date || '—']) tr.insertCell().textContent=value;
    const pill=document.createElement('span'); pill.className='status-pill'+(row.done?' done':'');
    pill.textContent=row.done?'Selesai':'Belum selesai'; tr.insertCell().append(pill);
    const cell=tr.insertCell(); const actions=document.createElement('div'); actions.className='table-actions';
    for(const [label,callback] of [['Buka',()=>callbacks.open(row)],
      [row.done?'Batalkan':'Selesai',()=>callbacks.status(row)],['Ekspor',()=>callbacks.export(row)]]) {
      const button=document.createElement('button');button.type='button';button.className='secondary';
      button.textContent=label;button.addEventListener('click',action(callback));actions.append(button);
    }
    cell.append(actions);
  }
  wrap.append(grid);target.append(wrap);
}
// Textarea menormalisasi CRLF. Simpan isi file/asli di memori sampai pengguna mengedit.
export function exactText(id) {
  const input=$(id); let original=null;
  input.addEventListener('input',()=>original=null);
  return { get:()=>original === null ? input.value : original,
    set(value){ original=value; input.value=value; }, clear(){original=null;input.value='';} };
}
