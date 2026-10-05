import {api} from './api.js';
import {$,keys,toast,action,download,fileText,exactText} from './ui.js';
let current=null, previousKeys=null, unlocked=false, refresh;
const contents = exactText('note-text'); const follow = exactText('follow-up');
const topic = exactText('note-topic');
export function openEditor(row) {
  $('note-form').reset(); current=row; previousKeys=null; unlocked=!row.id;
  contents.clear();follow.clear();topic.clear();
  $('note-heading').textContent=`${row.id?'Catatan sesi':'Catatan baru'} · ${row.code}`;
  const now=new Date();now.setMinutes(now.getMinutes()-now.getTimezoneOffset());
  $('session-date').value=row.session_date || now.toISOString().slice(0,10);
  $('next-date').value=row.next_date || '';
  $('note-fields').disabled=!unlocked; $('save-note').disabled=!unlocked;
  $('unlock-note').hidden=unlocked;
  $('note-status').textContent=unlocked?'Isi catatan dan kunci untuk menyimpan.':'Catatan terkunci. Masukkan tiga kunci untuk membukanya.';
  $('note-dialog').showModal();
}
export const callbacks = {
  open: openEditor,
  async status(row) {await api('sessions/status',{id:row.id,done:!row.done});await refresh();toast('Status tindak lanjut diperbarui.');},
  async export(row) {const pack=await api('sessions/export',{id:row.id});download(`catatan-${row.code}-${row.id}.json`,JSON.stringify(pack,null,2));toast('Paket tersandi diekspor tanpa kunci.');}
};
export function initNotes(onRefresh) {
  refresh=onRefresh;
  $('unlock-note').addEventListener('click',action(async()=>{
    const entered=keys('note-keys'); const payload=await api('sessions/open',{id:current.id,keys:entered});
    previousKeys=entered;unlocked=true;topic.set(payload.topic);contents.set(payload.notes);follow.set(payload.follow_up);
    $('note-fields').disabled=false;$('save-note').disabled=false;$('unlock-note').hidden=true;
    $('note-status').textContent='Catatan terbuka. Kunci saat simpan dipakai untuk enkripsi ulang.';
  }));
  let saving=false;
  $('note-form').addEventListener('submit',action(async()=>{
    if(!unlocked || saving) return;
    saving=true;$('save-note').disabled=true;
    try {
      await api('sessions/save',{id:current.id || null,client_id:current.client_id,
        session_date:$('session-date').value,next_date:$('next-date').value,
        topic:topic.get(),notes:contents.get(),follow_up:follow.get(),
        keys:keys('note-keys'),previous_keys:previousKeys});
      $('note-dialog').close();await refresh();toast('Catatan tersimpan. Validasi dekripsi identik berhasil.');
    } finally {saving=false;$('save-note').disabled=!unlocked;}
  }));
  $('note-file').addEventListener('change',action(async()=>contents.set(await fileText($('note-file')))));
  $('note-dialog').addEventListener('close',()=>{
    $('note-form').reset();contents.clear();follow.clear();topic.clear();
    current=null;previousKeys=null;unlocked=false;
    for(const field of $('note-keys').querySelectorAll('[data-key]')) field.type='password';
  });
  $('import-button').addEventListener('click',()=>{$('import-form').reset();$('import-dialog').showModal();});
  let importing=false;
  $('import-form').addEventListener('submit',action(async()=>{
    if(importing)return; importing=true;
    const submit=$('import-form').querySelector('[type=submit]');submit.disabled=true;
    try {
      let pack;try{pack=JSON.parse(await fileText($('package-file')));}catch(error){throw new Error('File bukan paket JSON UTF-8 yang valid.');}
      await api('sessions/import',{package:pack,keys:keys('import-keys')});
      $('import-dialog').close();await refresh();toast('Paket diverifikasi dan ditambahkan sebagai sesi baru.');
    }finally{importing=false;submit.disabled=false;}
  }));
  $('import-dialog').addEventListener('close',()=>{
    $('import-form').reset();for(const field of $('import-keys').querySelectorAll('[data-key]'))field.type='password';
  });
}
