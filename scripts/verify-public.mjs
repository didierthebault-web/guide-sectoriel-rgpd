import fs from 'node:fs/promises';import crypto from 'node:crypto';
const base='https://didierthebault-web.github.io/guide-sectoriel-rgpd/';const guide=JSON.parse(await fs.readFile('src/data/guide.json','utf8'));const checks=[];
for(const route of ['',...['I','II','III','IV','V','VI','VII'].map(p=>'parties/'+p.toLowerCase()+'/'),'fiches/','outils/','concertation/','validations/','recherche/','sections/III-fiche-01/','pagefind/pagefind.js','issues-snapshot.json','fulbi-logo.png','documents/'+guide.source]){
 const r=await fetch(base+route,{signal:AbortSignal.timeout(30000)});if(!r.ok)throw Error(route+' '+r.status);const bytes=Buffer.from(await r.arrayBuffer());if(route===''){const html=bytes.toString();if(!html.includes('/guide-sectoriel-rgpd/fulbi-logo.png'))throw Error('Logo absent');}
 if(route==='documents/'+guide.source&&crypto.createHash('sha256').update(bytes).digest('hex')!==guide.sourceSha256)throw Error('Word différent de la source');
 if(route==='fulbi-logo.png'){const local=await fs.readFile('public/fulbi-logo.png');if(!local.equals(bytes))throw Error('Logo public différent du fichier fourni');}
 checks.push({route,status:r.status,bytes:bytes.length});
}
const result={result:'PASS',checkedAt:new Date().toISOString(),url:base,checks,sourceSha256:guide.sourceSha256,logo:'Identique au fichier fourni',note:'Contrôle HTTP réel après le déploiement GitHub Pages.'};await fs.writeFile('reports/deployment.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
