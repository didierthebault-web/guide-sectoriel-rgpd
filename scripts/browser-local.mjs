import fs from 'node:fs';import path from 'node:path';
// Optional reuse of an installed Chromium; CI can install Playwright's pinned version.
if(!process.env.CHROMIUM_EXECUTABLE&&process.platform==='win32'){
 const cache=path.join(process.env.LOCALAPPDATA||'','ms-playwright');
 if(fs.existsSync(cache))for(const folder of fs.readdirSync(cache).filter(x=>/^chromium-\d+$/.test(x)).sort().reverse()){
  const candidate=path.join(cache,folder,'chrome-win64','chrome.exe');if(fs.existsSync(candidate)){process.env.CHROMIUM_EXECUTABLE=candidate;break;}
 }
}
await import('./browser-check.mjs');
