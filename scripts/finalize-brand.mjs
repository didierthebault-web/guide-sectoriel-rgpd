import fs from 'node:fs';
const p='src/layouts/Layout.astro';let s=fs.readFileSync(p,'utf8');
s=s.replace('<span class="wordmark">fulbi<span class="brand-dot">.</span></span><span class="brand-description">Fédération des utilisateurs<br/>de logiciels pour bibliothèques</span>','<img class="fulbi-logo" src={`${b}/fulbi-logo.png`} alt="FULBI — Fédération des Utilisateurs de Logiciels pour Bibliothèques, Information et Documentation" width="2490" height="820"/>');
s=s.replace('<span class="wordmark">fulbi<span class="brand-dot">.</span></span>','<img class="fulbi-logo footer-logo" src={`${b}/fulbi-logo.png`} alt="FULBI" width="2490" height="820" loading="lazy"/>');fs.writeFileSync(p,s);
const home='src/pages/index.astro';fs.writeFileSync(home,fs.readFileSync(home,'utf8').replace("p.id.padStart(2,'0')",'p.id'));
const about='src/pages/a-propos.astro';fs.writeFileSync(about,fs.readFileSync(about,'utf8').replace('Fédération des utilisateurs de logiciels pour bibliothèques','Fédération des Utilisateurs de Logiciels pour Bibliothèques, Information & Documentation'));
