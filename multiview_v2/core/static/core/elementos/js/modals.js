
// util genérico
export function openDialog(dlg){ try{ dlg.showModal?.() ?? (dlg.open=true);}catch{ dlg.open=true; } }
export function closeDialog(dlg){ try{ dlg.close?.(); }catch{ dlg.open=false; } }

// binder genérico para helps
export function bindHelp(btnId, dlgId){
  const btn = document.getElementById(btnId);
  const dlg = document.getElementById(dlgId);
  if(!btn || !dlg) return;
  btn.addEventListener('click', (e)=>{ e.preventDefault(); e.stopPropagation(); openDialog(dlg); });
  dlg.addEventListener('click', (e)=>{ if (e.target.closest('.js-close-help') || e.target === dlg) closeDialog(dlg); });
  document.addEventListener('keydown', (e)=>{ if (e.key === 'Escape' && (dlg.open || dlg.hasAttribute('open'))) closeDialog(dlg); });
}
