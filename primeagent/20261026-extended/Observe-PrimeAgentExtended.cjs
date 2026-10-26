// Observe the already-running Sudoku task; do not send another prompt or change its work.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {chromium}=require('C:/Users/asaad/AppData/Roaming/npm/node_modules/@qwen-code/qwen-code/bundled/browser-use/runtime/node_modules/playwright-core');
const dir=path.resolve(process.argv[2]),file=path.join(dir,'browser-verification.json');
const report=JSON.parse(fs.readFileSync(file,'utf8')),attempt=report.attempts.find(a=>a.task==='sudoku');
const delay=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1650,height:1100},acceptDownloads:true});
 try{
  await page.goto(attempt.sessionUrl);let loops=0;
  while(true){
   const text=await page.locator('body').innerText();
   const status=await(await page.request.get(attempt.sessionUrl.split('?')[0]+'/status')).json();
   const download=page.getByRole('button',{name:'Download',exact:true}).last();
   if(await download.isVisible() && !(await page.locator('[aria-label="esc to cancel"]').count()))break;
   if(!status.hasActivePrompt&&!status.hasRunningBackgroundTasks)break;
   if(++loops%6===0)console.log(JSON.stringify({observing:'existing Sudoku turn',active:status.hasActivePrompt,background:status.hasRunningBackgroundTasks,hasTurnError:status.hasTurnError,download:await download.isVisible()}));
   await delay(5000);
  }
  const status=await(await page.request.get(attempt.sessionUrl.split('?')[0]+'/status')).json();
  const transcript=await(await page.request.get(attempt.sessionUrl.split('?')[0]+'/transcript?limit=500')).json();
  let next=transcript;
  while(next.hasMore&&next.nextCursor){next=await(await page.request.get(attempt.sessionUrl.split('?')[0]+'/transcript?limit=500&cursor='+encodeURIComponent(next.nextCursor))).json();transcript.events.push(...next.events);}
  transcript.hasMore=next.hasMore;
  fs.writeFileSync(path.join(dir,'sudoku-reobserved-transcript.private.json'),JSON.stringify(transcript,null,2));
  attempt.previousObserverError=attempt.observerError;delete attempt.observerError;
  attempt.nativeHasTurnError=status.hasTurnError;
  attempt.hasTurnError=status.hasTurnError;
  attempt.reobservedAtUtc=new Date().toISOString();attempt.observationOnlyNoNewPrompt=true;
  attempt.tools=transcript.events.filter(e=>e.data?._meta?.toolName).map(e=>({tool:e.data._meta.toolName,status:e.data.status,title:e.data.title,output:e.data.rawOutput}));
  attempt.answer=transcript.events.filter(e=>e.data?.sessionUpdate==='agent_message_chunk').map(e=>e.data.content?.text||'').join('');
  attempt.transcriptHasMore=transcript.hasMore;
  const button=page.getByRole('button',{name:'Download',exact:true}).last();
  if(await button.isVisible()){
   const pending=page.waitForEvent('download');await button.click();const download=await pending;
   const destination=path.join(dir,'downloaded-sudoku.html');await download.saveAs(destination);
   attempt.download={filename:download.suggestedFilename(),bytes:fs.statSync(destination).size,sha256:crypto.createHash('sha256').update(fs.readFileSync(destination)).digest('hex')};
  }else attempt.observerError='The completed original turn did not provide a Download button.';
  attempt.completed=!attempt.hasTurnError&&!attempt.observerError;
  await page.screenshot({path:path.join(dir,'sudoku-reobserved-conversation.png'),clip:{x:270,y:130,width:1000,height:850}});
  const visible=await page.locator('body').innerText();fs.writeFileSync(path.join(dir,'sudoku-visible-final.private.txt'),visible);
  fs.writeFileSync(file,JSON.stringify(report,null,2));
  console.log(JSON.stringify({completed:attempt.completed,nativeHasTurnError:status.hasTurnError,download:attempt.download,transcriptHasMore:transcript.hasMore,tail:visible.slice(-4500)}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
