const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const { chromium } = require('C:/Users/asaad/AppData/Roaming/npm/node_modules/@qwen-code/qwen-code/bundled/browser-use/runtime/node_modules/playwright-core');
const root = __dirname;
const policy = JSON.parse(fs.readFileSync(path.join(root, 'campaign-policy.json'), 'utf8'));
assert.equal(policy.targets['primeagent-local-quality'].decision, 'allowed');
const planFlag = process.argv.indexOf('--plan');
const directory = planFlag >= 0 ? path.dirname(path.resolve(process.argv[planFlag + 1])) : fs.readFileSync(path.join(root, 'primeagent-quality/latest.txt'), 'utf8').trim();
const plan = JSON.parse(fs.readFileSync(path.join(directory, 'plan.json'), 'utf8'));
const repaired = process.argv.includes('--after-workspace-fix');
const suffix = repaired ? '-after-workspace-fix' : '';
const tasks = repaired ? ['documents', 'presentation'] : plan.tasks;
const report = { startedAtUtc: new Date().toISOString(), phase: repaired ? 'after-workspace-fix' : 'original', evaluation: plan.type, operator: 'Asaad AlSharif', application: 'PrimeAgent', interface: 'actual HTTPS browser composer', speedBenchmark: false, attempts: [], state: 'running' };
const save = () => fs.writeFileSync(path.join(directory, `browser-verification${suffix}.json`), JSON.stringify(report, null, 2));
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
(async () => {
  const browser = await chromium.launch({ executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless: true });
  const page = await browser.newPage({ viewport: { width: 1650, height: 1100 }, acceptDownloads: true });
  try {
    report.sourceModel = (await (await page.request.get('https://aipc/strata/v1/models')).json()).data.find(row => row.status?.value === 'loaded');
    assert(report.sourceModel, 'A source-advertised model must already be loaded.');
    for (const task of tasks) {
      const attempt = { task, startedAtUtc: new Date().toISOString(), errors: [], completed: false };
      report.attempts.push(attempt); save();
      const onError = error => attempt.errors.push(error.message);
      page.on('pageerror', onError);
      try {
        if (task === 'presentation' && !fs.existsSync(path.join(plan.workspace, 'documents/invoice-result.json'))) {
          attempt.blocked = 'The preceding invoice task produced no source JSON.'; continue;
        }
        await page.goto('https://aipc/', { waitUntil: 'domcontentloaded' });
        const selector = page.getByRole('button', { name: /^Select Model: / });
        await selector.waitFor();
        assert((await selector.getAttribute('aria-label')).includes(report.sourceModel.id), 'Keep the existing selected model; do not change global defaults.');
        assert.equal(await page.getByRole('button', { name: 'Approval mode', exact: true }).innerText(), 'Full Access');
        const created = [];
        const observeCreate = request => {
          if (request.method() === 'POST' && new URL(request.url()).pathname === '/session') {
            const body = request.postDataJSON();
            created.push({ model: body.model, approvalMode: body.approvalMode, workspaceId: body.workspaceId, cwd: body.cwd });
          }
        };
        page.on('request', observeCreate);
        await page.locator('[contenteditable=true][role=textbox]').fill(plan.prompts[task]);
        await page.getByRole('button', { name: 'Send message', exact: true }).click();
        await page.waitForURL(/\/session\//);
        page.off('request', observeCreate);
        attempt.sessionUrl = page.url(); attempt.creation = created;
        console.log(JSON.stringify({ task, sessionUrl: attempt.sessionUrl, state: 'submitted through browser' })); save();
        const sessionId = new URL(page.url()).pathname.split('/').pop();
        let polls = 0;
        while (true) {
          const visible = await page.locator('body').innerText();
          if (visible.includes('Processed') && !await page.locator('[aria-label="esc to cancel"]').count()) break;
          await delay(5000);
          if (++polls % 6 === 0) console.log(JSON.stringify({ task, state: 'agent working', observedAtUtc: new Date().toISOString() }));
          const status = await (await page.request.get(`https://aipc/session/${sessionId}/status`)).json();
          if (status.hasTurnError && !status.hasActivePrompt && !status.hasRunningBackgroundTasks) { attempt.turnError = true; break; }
        }
        const status = await (await page.request.get(`https://aipc/session/${sessionId}/status`)).json();
        attempt.workspaceCwd = status.workspaceCwd; attempt.hasTurnError = status.hasTurnError;
        const transcript = await (await page.request.get(`https://aipc/session/${sessionId}/transcript?limit=500`)).json();
        let transcriptPage = transcript;
        while (transcriptPage.hasMore && transcriptPage.nextCursor) {
          transcriptPage = await (await page.request.get(`https://aipc/session/${sessionId}/transcript?limit=500&cursor=${encodeURIComponent(transcriptPage.nextCursor)}`)).json();
          transcript.events.push(...transcriptPage.events);
        }
        transcript.hasMore = transcriptPage.hasMore;
        fs.writeFileSync(path.join(directory, `${task}${suffix}-transcript.private.json`), JSON.stringify(transcript, null, 2));
        attempt.tools = transcript.events.filter(event => event.data?._meta?.toolName).map(event => ({ tool: event.data._meta.toolName, status: event.data.status, title: event.data.title, output: event.data.rawOutput }));
        attempt.answer = transcript.events.filter(event => event.data?.sessionUpdate === 'agent_message_chunk').map(event => event.data.content?.text || '').join('');
        attempt.completed = !attempt.hasTurnError;
        assert.equal(path.resolve(status.workspaceCwd).toLowerCase(), path.resolve(JSON.parse(fs.readFileSync(path.join(root, '../portal.config.json'), 'utf8')).agentWorkspace).toLowerCase());
        // Screenshot only this test's central conversation, excluding other session titles.
        await page.screenshot({ path: path.join(directory, `${task}${suffix}-conversation.png`), clip: { x: 270, y: 130, width: 1000, height: 850 } });
        if (task === 'presentation' || plan.downloads?.[task]) {
          const button = page.getByRole('button', { name: 'Download', exact: true }).last();
          if (!await button.isVisible() && plan.downloads?.[task] === '.html') {
            await page.getByRole('button', { name: 'Toggle environment information', exact: true }).click();
            const artifact = page.getByRole('button', { name: new RegExp('^' + task + '\\.html') }).last();
            if (await artifact.isVisible()) await artifact.click();
          }
          await button.waitFor({ timeout: 15000 });
          const pending = page.waitForEvent('download');
          await button.click();
          const download = await pending;
          const filename = download.suggestedFilename();
          const extension = plan.downloads?.[task] || '.pptx';
          assert(filename.toLowerCase().endsWith(extension));
          const destination = path.join(directory, `downloaded-${task}${extension}`);
          await download.saveAs(destination);
          attempt.download = { filename, bytes: fs.statSync(destination).size, sha256: crypto.createHash('sha256').update(fs.readFileSync(destination)).digest('hex') };
        }
        console.log(JSON.stringify({ task, state: 'finished', turnError: attempt.hasTurnError, tools: attempt.tools.map(row => ({tool:row.tool,status:row.status})), downloaded: !!attempt.download }));
      } catch (error) {
        attempt.observerError = error.stack;
        console.error(JSON.stringify({ task, error: error.message }));
        await page.screenshot({ path: path.join(directory, `${task}${suffix}-observation-failure.png`), clip: { x: 270, y: 130, width: 1000, height: 850 } }).catch(() => {});
      } finally {
        page.off('pageerror', onError);
        attempt.finishedAtUtc = new Date().toISOString(); save();
      }
    }
    report.state = 'browser-complete';
  } catch (error) { report.state = 'observer-failed'; report.error = error.stack; process.exitCode = 1; console.error(error.message); }
  finally { report.finishedAtUtc = new Date().toISOString(); save(); await browser.close(); console.log(JSON.stringify({state:report.state,directory})); }
})();
