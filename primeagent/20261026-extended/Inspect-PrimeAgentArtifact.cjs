const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {chromium}=require('C:/Users/asaad/AppData/Roaming/npm/node_modules/@qwen-code/qwen-code/bundled/browser-use/runtime/node_modules/playwright-core');
const dir=path.resolve(process.argv[2]);
(async()=>{const b=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
try{const p=await b.newPage({viewport:{width:1650,height:1100},acceptDownloads:true});await p.goto('https://aipc/session/38bc6611-0960-4220-9015-ea3b82f4bcbb');await p.waitForTimeout(1500);
await p.getByRole('button',{name:'Toggle environment information',exact:true}).click();await p.waitForTimeout(500);
await p.getByRole('button',{name:'sudoku.html — playable self-contained Sudoku',exact:true}).click();await p.waitForTimeout(500);
console.log(JSON.stringify(await p.locator('button,a').evaluateAll(es=>es.filter(e=>{const r=e.getBoundingClientRect();return r.x>270&&r.width>0&&r.height>0;}).map(e=>({tag:e.tagName,text:e.innerText.slice(0,100),label:e.getAttribute('aria-label'),title:e.getAttribute('title'),href:e.getAttribute('href')}))),null,2));
console.log('PANEL '+(await p.locator('body').innerText()).slice(-2000));
await p.screenshot({path:path.join(dir,'artifact-panel-open.png'),clip:{x:270,y:65,width:1380,height:1000}});
const button=p.getByRole('button',{name:'Download',exact:true}).last();
if(await button.isVisible()){
 const pending=p.waitForEvent('download');await button.click();const d=await pending;const destination=path.join(dir,'downloaded-sudoku.html');await d.saveAs(destination);
 const reportFile=path.join(dir,'browser-verification.json'),report=JSON.parse(fs.readFileSync(reportFile,'utf8')),attempt=report.attempts.find(a=>a.task==='sudoku');
 attempt.download={filename:d.suggestedFilename(),bytes:fs.statSync(destination).size,sha256:crypto.createHash('sha256').update(fs.readFileSync(destination)).digest('hex')};
 attempt.downloadWorkflow='Toggle environment information > sudoku.html artifact > Download';delete attempt.observerError;
 fs.writeFileSync(reportFile,JSON.stringify(report,null,2));console.log(JSON.stringify({download:attempt.download}));
}
}finally{await b.close();}})();
