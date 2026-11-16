export const REPO='didierthebault-web/guide-sectoriel-rgpd';
export const PARTS=['I','II','III','IV','V','VI','VII'];
export const TYPES={juridique:'Observation juridique',editorial:'Correction éditoriale',terminologie:'Correction terminologique',contradiction:'Contradiction entre sections',complement:'Proposition de complément',technique:'Problème technique'};
export const STATUSES={'a-instruire':'À instruire','a-completer':'À compléter',retenue:'Retenue','non-retenue':'Non retenue',integree:'Intégrée'};
export const LABELS=[...Object.keys(TYPES).map(x=>'type:'+x),...Object.keys(STATUSES).map(x=>'statut:'+x),...PARTS.map(x=>'partie:'+x)];
export const WARNING="Les observations déposées sur GitHub Issues sont publiques. Elles peuvent être consultées par toute personne et restent associées au compte GitHub utilisé. Ne publiez pas de données personnelles, d'informations confidentielles ou de documents non destinés à la diffusion.";
export function contribution(data){
 const title=`[Partie ${data.part}][Section ${data.id}] ${TYPES[data.type]} — ${data.title}`;
 const body=[['Partie',data.part],['Identifiant de section',data.id],['Titre de la section',data.title],['URL permanente',data.url],['Version du texte',data.version],['Type d’observation',TYPES[data.type]],['Passage concerné',data.passage||'Non précisé'],['Constat',data.description],['Modification proposée',data.proposal],['Justification ou référence',data.justification||'Non précisée']].map(([k,v])=>`## ${k}\n${v}`).join('\n\n');
 const params=new URLSearchParams({title,body,labels:['type:'+data.type,'statut:a-instruire',...(PARTS.includes(data.part)?['partie:'+data.part]:[])].join(',')});
 const url=`https://github.com/${REPO}/issues/new?${params}`;
 return {title,body,url,tooLong:url.length>7500,text:title+'\n\n'+body};
}
export function summarize(issues){const count=(prefix,keys)=>Object.fromEntries(keys.map(k=>[k,issues.filter(x=>x.labels.includes(prefix+k)).length]));return {total:issues.length,open:issues.filter(x=>x.state==='open').length,status:count('statut:',Object.keys(STATUSES)),parts:count('partie:',PARTS),types:count('type:',Object.keys(TYPES))};}
export function validationFor(section,record){return record?.contentHash===section.hash?record.status:'À réexaminer';}
