import { contribution } from './issues.mjs';
const dialog=document.querySelector<HTMLDialogElement>('#observation-dialog')!;
const form=document.querySelector<HTMLFormElement>('#observation-form')!;
let opener:HTMLElement|null=null;
document.querySelectorAll<HTMLButtonElement>('[data-observe]').forEach(button=>button.addEventListener('click',()=>{
 opener=button;form.reset();document.querySelector<HTMLElement>('#observation-result')!.hidden=true;
 for(const key of ['part','id','title','version']) (form.elements.namedItem(key) as HTMLInputElement).value=button.dataset[key]||'';
 (form.elements.namedItem('url') as HTMLInputElement).value=new URL(button.dataset.url!,location.origin).href;
 dialog.showModal();
}));
document.querySelector('.close')?.addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>opener?.focus());
form.addEventListener('submit',event=>{event.preventDefault();if(!form.reportValidity())return;const data=Object.fromEntries(new FormData(form));
 for(const k of ['description','proposal']){const input=form.elements.namedItem(k) as HTMLTextAreaElement;if(!input.value.trim()){input.setCustomValidity('Veuillez renseigner ce champ.');input.reportValidity();input.addEventListener('input',()=>input.setCustomValidity(''),{once:true});return;}}
 const result=contribution(data);const box=document.querySelector<HTMLTextAreaElement>('#observation-copy')!;box.value=result.text;
 const link=document.querySelector<HTMLAnchorElement>('#github-publish')!;link.href=result.tooLong?'https://github.com/didierthebault-web/guide-sectoriel-rgpd/issues/new':result.url;
 document.querySelector('#observation-message')!.textContent=result.tooLong?'Contribution longue : copiez le texte ci-dessous puis collez-le dans l’issue vide.':'Contribution prête. La publication définitive se fait sur GitHub après connexion.';
 document.querySelector<HTMLElement>('#observation-result')!.hidden=false;box.scrollIntoView({block:'center'});
});
async function copy(value:string,fallback?:HTMLTextAreaElement){try{await navigator.clipboard.writeText(value);document.querySelector('#live-message')!.textContent='Texte copié.';return true;}catch{fallback?.focus();fallback?.select();document.querySelector('#live-message')!.textContent='Sélectionnez le texte et utilisez Ctrl+C pour le copier.';return false;}}
document.querySelector('#copy-observation')?.addEventListener('click',async()=>{const box=document.querySelector<HTMLTextAreaElement>('#observation-copy')!;const ok=await copy(box.value,box);document.querySelector('#observation-message')!.textContent=ok?'Contribution copiée.':'Copie automatique indisponible : le texte est sélectionné. Utilisez Ctrl+C ou la commande Copier.';});
document.querySelectorAll<HTMLButtonElement>('[data-copy-link]').forEach(button=>button.addEventListener('click',async()=>{const url=new URL(button.dataset.copyLink!,location.origin).href;if(await copy(url))button.textContent='Lien copié ✓';else{const input=document.createElement('input');input.value=url;input.setAttribute('aria-label','Lien permanent à copier');button.after(input);input.focus();input.select();}}));
document.querySelectorAll<HTMLButtonElement>('[data-font]').forEach(button=>button.addEventListener('click',()=>{const current=parseInt(getComputedStyle(document.documentElement).getPropertyValue('--read-size'))||18;document.documentElement.style.setProperty('--read-size',Math.max(15,Math.min(26,current+Number(button.dataset.font)))+'px');}));
document.querySelector('[data-print]')?.addEventListener('click',()=>window.print());
function progress(){const bar=document.querySelector<HTMLElement>('.progress-bar');if(bar)bar.style.width=(100*window.scrollY/Math.max(1,document.documentElement.scrollHeight-innerHeight))+'%';}addEventListener('scroll',progress,{passive:true});progress();
if(innerWidth<701)document.querySelectorAll<HTMLDetailsElement>('.side-nav details,.local-nav details').forEach(x=>x.open=false);
