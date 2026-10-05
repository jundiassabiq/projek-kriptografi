import {api,bootstrap} from './api.js';
import {$,toast,action,table,setupKeyVisibility} from './ui.js';
import {initNotes,callbacks,openEditor} from './notes.js';
import {initDemo} from './demo.js';
let selected=null,clients=[],refreshSerial=0;
async function refresh() {
  const serial=++refreshSerial;
  const [dashboard,list]=await Promise.all([api('dashboard'),api('clients?search='+encodeURIComponent($('search-client').value))]);
  if(serial!==refreshSerial)return;
  clients=list;
  for(const field of ['clients','sessions','pending'])$('count-'+field).textContent=dashboard[field];
  table('pending-table',dashboard.records,callbacks);
  if(selected && !clients.some(row=>row.id===selected))selected=null;
  renderClients();await refreshSessions();
}
function renderClients() {
  const target=$('client-list');target.replaceChildren();
  if(!clients.length){const text=document.createElement('p');text.className='empty';text.textContent='Belum ada klien. Tambahkan kode samaran.';target.append(text);}
  for(const row of clients){
    const button=document.createElement('button');button.type='button';button.className='client-item'+(selected===row.id?' selected':'');
    button.textContent=row.code;button.addEventListener('click',action(async()=>{selected=row.id;renderClients();await refreshSessions();}));target.append(button);
  }
}
async function refreshSessions() {
  const row=clients.find(client=>client.id===selected);
  $('selected-client').textContent=row?'Riwayat · '+row.code:'Pilih klien';$('new-session').disabled=!row;
  if(!row){table('sessions-table',[],callbacks);return;}
  const id=row.id;const records=await api('sessions?client_id='+id);
  if(selected===id)table('sessions-table',records,callbacks);
}
for(const button of document.querySelectorAll('[data-view]')){
  button.addEventListener('click',()=>{
    for(const view of document.querySelectorAll('.view'))view.hidden=view.id!==button.dataset.view;
    for(const nav of document.querySelectorAll('.nav'))nav.classList.toggle('active',nav===button);
  });
}
for(const button of document.querySelectorAll('[data-close]'))button.addEventListener('click',()=>$(button.dataset.close).close());
setupKeyVisibility();initNotes(refresh);initDemo();
$('refresh').addEventListener('click',action(refresh));
let timer;$('search-client').addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(action(refresh),180);});
$('client-form').addEventListener('submit',action(async()=>{
  const result=await api('clients',{code:$('new-code').value});selected=result.id;$('new-code').value='';$('search-client').value='';
  await refresh();toast('Klien ditambahkan.');
}));
$('new-session').addEventListener('click',()=>{
  const row=clients.find(client=>client.id===selected);if(row)openEditor({client_id:row.id,code:row.code});
});
try{await bootstrap();await refresh();}catch(error){toast('Tidak bisa terhubung: '+error.message,true);}
