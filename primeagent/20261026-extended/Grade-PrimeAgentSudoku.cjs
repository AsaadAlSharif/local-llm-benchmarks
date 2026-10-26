const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),http=require('node:http');
const {chromium}=require('C:/Users/asaad/AppData/Roaming/npm/node_modules/@qwen-code/qwen-code/bundled/browser-use/runtime/node_modules/playwright-core');
const dir=path.resolve(process.argv[2]),plan=JSON.parse(fs.readFileSync(path.join(dir,'plan.json'),'utf8'));
const generated=path.join(plan.workspace,'sudoku/sudoku.html'),download=path.join(dir,'downloaded-sudoku.html');
const checks=[],errors=[];let browser,server;
const check=async(name,fn)=>{try{await fn();checks.push({name,passed:true});}catch(e){checks.push({name,passed:false,error:e.message});}};
(async()=>{
await check('Browser Download matches generated file byte for byte',async()=>assert(fs.readFileSync(download).equals(fs.readFileSync(generated))));
if(!fs.existsSync(generated))throw Error('No Sudoku HTML produced');
server=http.createServer((req,res)=>{res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(fs.readFileSync(generated));});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
const page=await browser.newPage({viewport:{width:1100,height:900}});page.on('pageerror',e=>errors.push(e.message));
const origin=`http://127.0.0.1:${server.address().port}`;
const network=[];await page.route('**/*',route=>{const url=route.request().url();if(url.startsWith(origin+'/')||url.startsWith('data:'))return route.continue();network.push(url);return route.abort();});
await page.goto(origin);const cells=page.locator('input[data-row][data-col]');
const cell=(r,c)=>page.locator(`input[data-row="${r}"][data-col="${c}"]`);
const values=()=>cells.evaluateAll(es=>es.map(e=>e.value).join(''));
const board=()=>cells.evaluateAll(es=>es.map(e=>Number(e.value)||0));
const puzzle=fs.readFileSync(path.join(plan.workspace,'sudoku/puzzle.txt'),'utf8').trim();
const status=()=>page.getByRole('status').innerText();
const successful=t=>/congrat|success|solved|correct|complete/i.test(t)&& !/not|incomplete|incorrect|invalid|conflict/i.test(t);
await check('81 cells match source puzzle',async()=>{assert.equal(await cells.count(),81);assert.deepEqual(await board(),[...puzzle].map(Number));});
await check('Given cells are locked',async()=>{assert.equal(await cell(0,0).inputValue(),'5');assert(!(await cell(0,0).isEditable()));});
await check('Blank cells accept digits',async()=>{await cell(0,2).fill('4');assert.equal(await cell(0,2).inputValue(),'4');});
await check('Editable cells can be cleared',async()=>{await cell(0,2).fill('');assert.equal(await cell(0,2).inputValue(),'');});
await check('Letters are rejected',async()=>{await cell(0,2).focus();await page.keyboard.type('x');assert.equal(await cell(0,2).inputValue(),'');});
await check('Zero is rejected',async()=>{await cell(0,2).fill('0');assert.equal(await cell(0,2).inputValue(),'');});
await check('Incomplete puzzle is never reported solved',async()=>{await cell(0,2).fill('');await page.getByRole('button',{name:'Check',exact:true}).click();const t=await status();assert(t.trim());assert(!successful(t),t);assert(/incomplete|empty|remaining|fill|missing/i.test(t),t);});
await check('Conflicting entry is rejected by Check',async()=>{await cell(0,2).fill('5');await page.getByRole('button',{name:'Check',exact:true}).click();const t=await status();assert(!successful(t),t);assert(/conflict|invalid|incorrect|duplicate|error/i.test(t),t);});
await check('Reset restores original puzzle',async()=>{await page.getByRole('button',{name:'Reset',exact:true}).click();assert.deepEqual(await board(),[...puzzle].map(Number));});
for(const [key,r,c] of [['ArrowRight',0,3],['ArrowLeft',0,2],['ArrowDown',1,2],['ArrowUp',0,2]]){
  if(key==='ArrowRight')await cell(0,2).focus();
  await check(key+' focus movement',async()=>{await page.keyboard.press(key);assert(await cell(r,c).evaluate(el=>el===document.activeElement));});
}
await check('Solve produces a valid complete Sudoku preserving givens',async()=>{
 await page.getByRole('button',{name:'Solve',exact:true}).click();const a=await board();assert.equal(a.length,81);assert(a.every(x=>Number.isInteger(x)&&x>=1&&x<=9));
 const valid=xs=>assert.equal(new Set(xs).size,9);
 for(let i=0;i<9;i++){valid(a.slice(i*9,i*9+9));valid(Array.from({length:9},(_,j)=>a[j*9+i]));valid(Array.from({length:9},(_,j)=>a[(Math.floor(i/3)*3+Math.floor(j/3))*9+(i%3)*3+j%3]));}
 for(let i=0;i<81;i++)if(puzzle[i]!=='0')assert.equal(a[i],Number(puzzle[i]));
});
await check('Check recognizes completed solution',async()=>{await page.getByRole('button',{name:'Check',exact:true}).click();assert(successful(await status()));});
await check('Reset remains functional after Solve',async()=>{await page.getByRole('button',{name:'Reset',exact:true}).click();assert.deepEqual(await board(),[...puzzle].map(Number));assert(await cell(0,2).isEditable());});
await check('Phone width has no horizontal overflow',async()=>{await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));});
await check('No page script errors',async()=>assert.deepEqual(errors,[]));
await check('No external network dependencies',async()=>assert.deepEqual(network,[]));
await page.screenshot({path:path.join(dir,'sudoku-phone.png'),fullPage:true});
})().catch(e=>checks.push({name:'Browser workflow',passed:false,error:e.stack})).finally(async()=>{
if(browser)await browser.close();if(server)await new Promise(r=>server.close(r));
const result={checkedAtUtc:new Date().toISOString(),checks:checks.length,passed:checks.filter(c=>c.passed).length,failed:checks.filter(c=>!c.passed),details:checks};
fs.writeFileSync(path.join(dir,'independent-sudoku-verification.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify({checks:result.checks,passed:result.passed,failed:result.failed}));if(result.failed.length)process.exitCode=1;
});
