
// Máscara decimal simples e defensiva
export function maskDecimal(el){
  if(!el) return;
  el.setAttribute('inputmode','decimal');
  el.addEventListener('beforeinput',(e)=>{ const ok=/[\d\.\-]/; if(e.data && !ok.test(e.data)) e.preventDefault(); });
  el.addEventListener('input',()=>{ let v=el.value.replace(',', '.'); const p=v.split('.'); if(p.length>2) v=p.shift()+'.'+p.join(''); v=v.replace(/(?!^)-/g,''); el.value=v; });
}
