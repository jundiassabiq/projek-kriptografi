import {api} from './api.js';
import {$,keys,action,download,fileText,exactText} from './ui.js';
const plain=exactText('demo-plain'),cipher=exactText('demo-cipher');let hasBaseline=false;
function stages(result) {
  $('demo-stages').replaceChildren();
  result.stages.forEach(([name,value],index)=>{
    const card=document.createElement('div');card.className='stage';
    const heading=document.createElement('h3');heading.textContent=`${index+1}. ${name}`;
    const text=document.createElement('pre');text.textContent=value;
    card.append(heading,text);$('demo-stages').append(card);
  });
}
export function initDemo() {
  $('demo-encrypt').addEventListener('click',action(async()=>{
    const result=await api('demo',{action:'encrypt',text:plain.get(),keys:keys('demo-keys')});
    hasBaseline=true;cipher.set(result.text);stages(result);$('demo-result').value='';
    $('demo-status').className='';$('demo-status').textContent='Enkripsi selesai. Dekripsi untuk memeriksa kesamaan teks.';
  }));
  $('demo-decrypt').addEventListener('click',action(async()=>{
    const result=await api('demo',{action:'decrypt',text:cipher.get(),keys:keys('demo-keys')});
    stages(result);$('demo-result').value=result.text;
    if(!hasBaseline && plain.get()==='') {
      $('demo-status').className='';$('demo-status').textContent='Dekripsi selesai. Isi plainteks pembanding untuk memvalidasi.';
    }else{
      const same=result.text===plain.get();$('demo-status').className=same?'good':'bad';
      $('demo-status').textContent=same?'VALIDASI BERHASIL — dekripsi identik dengan teks awal.':'VALIDASI GAGAL — periksa kunci, cipherteks, dan teks pembanding.';
    }
  }));
  for(const [id,target] of [['plain-file',plain],['cipher-file',cipher]]) {
    $(id).addEventListener('change',action(async()=>{
      target.set(await fileText($(id)));hasBaseline=false;
      $('demo-stages').replaceChildren();$('demo-result').value='';
      $('demo-status').className='';$('demo-status').textContent='File dimuat. Jalankan proses untuk hasil terbaru.';
    }));
  }
  $('demo-download').addEventListener('click',()=>download('cipherteks.txt',cipher.get(),'text/plain;charset=utf-8'));
  $('demo-clear').addEventListener('click',()=>{
    plain.clear();cipher.clear();hasBaseline=false;$('demo-result').value='';$('demo-stages').replaceChildren();
    for(const field of $('demo-keys').querySelectorAll('[data-key]')){field.value='';field.type='password';}
    $('demo-keys').querySelector('[data-show-keys]').checked=false;
    $('plain-file').value='';$('cipher-file').value='';
    $('demo-status').className='';$('demo-status').textContent='Teks dan kunci dibersihkan.';
  });
}
