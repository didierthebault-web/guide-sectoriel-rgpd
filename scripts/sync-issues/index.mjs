import fs from 'node:fs/promises';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {REPO,summarize} from '../../src/utils/issues.mjs';
export async function collectIssues(fetcher=fetch,token=process.env.GITHUB_TOKEN){
 const all=[];let page=1;
 while(true){const response=await fetcher(`https://api.github.com/repos/${REPO}/issues?state=all&per_page=100&page=${page}`,{headers:{Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28',...(token?{Authorization:`Bearer ${token}`}:{})},signal:AbortSignal.timeout(30000)});
 if(!response.ok)throw Error(`GitHub ${response.status} : instantané précédent conservé`);const batch=await response.json();if(!Array.isArray(batch))throw Error('Réponse GitHub invalide');
 for(const x of batch){if(x.pull_request)continue;if(!Number.isInteger(x.number)||!['open','closed'].includes(x.state)||!Array.isArray(x.labels))throw Error('Issue invalide');all.push({number:x.number,title:String(x.title),url:`https://github.com/${REPO}/issues/${x.number}`,state:x.state,labels:x.labels.map(l=>typeof l==='string'?l:l.name),createdAt:x.created_at,updatedAt:x.updated_at,closedAt:x.closed_at,comments:x.comments});}
 if(batch.length<100)break;page++;if(page>10000)throw Error('Pagination excessive');
 }
 return all.sort((a,b)=>b.number-a.number);
}
export async function sync(){const issues=await collectIssues();const data={repository:REPO,syncedAt:new Date().toISOString(),issues,summary:summarize(issues)};const target=fileURLToPath(new URL('../../src/data/issues.json',import.meta.url));await fs.mkdir(fileURLToPath(new URL('../../src/data/',import.meta.url)),{recursive:true});await fs.writeFile(target+'.tmp',JSON.stringify(data,null,2)+'\n');await fs.rename(target+'.tmp',target);console.log(`Synchronisation : ${issues.length} issues, ${data.syncedAt}`);return data;}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)await sync();
