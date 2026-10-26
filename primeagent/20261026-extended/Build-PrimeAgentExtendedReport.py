"""Package measured pass/fail results without filtering out unsuccessful attempts."""
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

root=Path(__file__).resolve().parent;directory=Path(sys.argv[1]);load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
plan=load(directory/'plan.json');browser=load(directory/'browser-verification.json')
functional=load(directory/'independent-functional-verification.json');sudoku=load(directory/'independent-sudoku-verification.json');audit=load(directory/'strata-pr-audit.json')
workspace=Path(plan['workspace']);publication=root/'publication';package=publication/'primeagent/20261026-extended';package.mkdir(parents=True,exist_ok=True)
replacements=[(str(workspace.parent),'<agent-workspace>'),(str(root.parent),'<portal>')]
def clean(value):
    if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
    if isinstance(value,list):return [clean(v) for v in value]
    if isinstance(value,str):
        for old,new in replacements:value=value.replace(old,new).replace(old.replace('\\','/'),new)
    return value
def write_json(name,value):(package/name).write_text(json.dumps(clean(value),ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
def copy_file(source,relative):
    target=package/relative;target.parent.mkdir(parents=True,exist_ok=True)
    if source.suffix.lower() in ['.py','.cjs','.js','.mjs','.md','.json','.txt','.sql','.html']:
        target.write_text(source.read_text(encoding='utf-8-sig'),encoding='utf-8',newline='\n')
    else:shutil.copy2(source,target)
for name in ['plan.json','independent-functional-verification.json','independent-sudoku-verification.json','strata-pr-audit.json','sql-fixture.json']:
    write_json(name,load(directory/name))
for name in ['observer-certificate-attempt.json','final-health.json','environment.json','post-run-diagnosis.json','premature-functional-verification.json','premature-sudoku-verification.json']:
    if (directory/name).exists():write_json(name,load(directory/name))
summary={'application':'PrimeAgent','operator':'Asaad AlSharif','type':plan['type'],'model':browser['sourceModel'],'startedAtUtc':browser['startedAtUtc'],'finishedAtUtc':browser.get('finishedAtUtc'),'speedBenchmark':False,'attempts':[]}
for a in browser['attempts']:
    tool_summaries=[]
    for t in a.get('tools',[]):
        item={k:t.get(k) for k in ['tool','status','title']}
        if t['status']=='failed':item['failure']=str(t.get('output',''))[:4000]
        if a['task']=='sudoku' and t['tool']=='mcp__playwright__browser_evaluate' and t['status']=='completed':item['browserEvaluation']=t.get('output')
        tool_summaries.append(item)
    summary['attempts'].append({**{k:a.get(k) for k in ['task','sessionUrl','completed','hasTurnError','nativeHasTurnError','observerError','previousObserverError','observationOnlyNoNewPrompt','errors','download','answer']},'tools':tool_summaries,'failedToolEvents':sum(t['status']=='failed' for t in a.get('tools',[]))})
write_json('browser-summary.json',summary)
for source in (directory/'inputs').rglob('*'):
    if source.is_file():copy_file(source,source.relative_to(directory))
for task in ['repair','sql','sudoku','evidence']:
    for source in (workspace/task).iterdir():
        if source.is_file() and source.suffix.lower() in ['.py','.cjs','.js','.mjs','.html','.json','.sql']:
            copy_file(source,Path('generated')/task/source.name)
for name in ['Grade-PrimeAgentExtended.py','Grade-PrimeAgentSudoku.cjs']:
    assert hashlib.sha256((directory/name).read_bytes()).hexdigest()==plan['frozenGraderSha256'][name], 'Frozen grader changed'
    copy_file(directory/name,name)
for name in ['Prepare-PrimeAgentExtended.py','Run-PrimeAgentQuality.cjs','Build-PrimeAgentExtendedReport.py','campaign-policy.json']:copy_file(root/name,name)
for name in ['Observe-PrimeAgentExtended.cjs','Inspect-PrimeAgentArtifact.cjs','Diagnose-PrimeAgentExtended.py']:copy_file(root/name,name)
if (workspace/'result.json').exists():copy_file(workspace/'result.json','generated/misplaced-evidence-result.json')
for source in directory.glob('*.png'):copy_file(source,source.name)
if (directory/'downloaded-sudoku.html').exists():shutil.copy2(directory/'downloaded-sudoku.html',package/'PrimeAgent-Sudoku.html')
elif (workspace/'sudoku/sudoku.html').exists():shutil.copy2(workspace/'sudoku/sudoku.html',package/'PrimeAgent-Sudoku.html')
(package/'.gitattributes').write_text('PrimeAgent-Sudoku.html -text\n',encoding='utf-8',newline='\n')
rows=[];aggregate={}
for task in plan['tasks']:
    details=[d for d in functional['details'] if d['task']==task]
    if task=='sudoku':details+=sudoku['details']
    passed=sum(d['passed'] for d in details);aggregate[task]={'passed':passed,'checks':len(details),'failed':[d for d in details if not d['passed']]}
    a=next(x for x in summary['attempts'] if x['task']==task)
    rows.append(f"| {task} | {passed}/{len(details)} | {a['failedToolEvents']} | [LAN conversation]({a['sessionUrl']}) |")
write_json('summary.json',{'generatedAtUtc':datetime.now(timezone.utc).isoformat(),'model':browser['sourceModel']['id'],'taskResults':aggregate,'globalRank':None,'speedBenchmark':False})
failures='\n'.join(f"- {task}: {d['name']}: {d.get('error','failed')}" for task,info in aggregate.items() for d in info['failed']) or '- No independent functional checks failed.'
text=f'''# PrimeAgent extended functional evaluation

**Asaad AlSharif — PrimeAgent**, October 26, 2026.

Four new tasks were submitted through the normal HTTPS chat composer, using **{browser['sourceModel']['id']}** with its existing model settings. Inputs and independent grader hashes were frozen before the first task. These are custom functional evaluations, not a standardized leaderboard or a global rank. No speed benchmark, model switch, excluded-board run or default-setting change was made. Normal chat stayed available.

| Task | Independent checks passed | Failed tool-status events | Actual user-interface evidence |
|---|---:|---:|---|
{chr(10).join(rows)}

The tasks test decimal rounding/validation and code repair; SQLite join fan-out, invoice statuses and per-invoice overpayments; a real Sudoku browser interaction including incomplete/invalid board checks, solving, keyboard and phone layout; and conflicting Arabic documents where the latest draft must be excluded from approved totals. Check counts represent different assertions, not independent benchmark questions or comparable model scores. A completed shell-tool event is not by itself proof that its command succeeded; independent output checks determine the result.

## Failures and limits

{failures}

The first automation launch stopped before any model request because Node did not use the installed local certificate authority. That observer failure is retained in `observer-certificate-attempt.json`; retry used Node's `--use-system-ca` and preserved certificate validation. There was one initial agent turn per task. Self-corrections within that turn are retained in the tool-event summaries. Codex did not repair the generated implementations or feed grader failures back to the model.

The first Sudoku observer also stopped early on a native error flag while the agent continued working. Its premature grader reports are retained but superseded by the final unchanged graders, run after the original turn completed. Observation was corrected to consider active/background state and to page the full transcript. The Arabic task briefly overlapped the tail of Sudoku because of that observer error; no timing or controlled speed claim is made. No additional agent request was sent to improve the Sudoku result.

**Diagnosis:** The repair and SQL tasks passed their frozen independent checks. Sudoku passed 18 of 19 game/browser checks, but pasted `0` remained in a cell. Its native artifact was registered and opened as a playable HTML preview; no Download control was available in the conversation, environment panel or opened artifact panel, so portal Download/byte equality did not pass. Native session status still reported `hasTurnError=true` after the agent finished and stopped its test servers; its exact cause is not established. The public Sudoku below is copied from the generated file, not claimed as a portal download.

The Arabic task read all three sources and made four successful math calls. Its result has the correct schema and all twelve values, but it wrote `result.json` in the test root instead of `evidence/result.json`. The required-path check therefore failed and dependent field checks in the frozen grader were not executed. `post-run-diagnosis.json` and `generated/misplaced-evidence-result.json` preserve the separate content verification without converting this delivery failure into a pass. The source DOCX files were unchanged.

Arabic evidence uses locally generated DOCX text, not scanned-PDF OCR. Sudoku uses one fixed starting puzzle; random generation/difficulty calibration are not tested. These results do not cover the entire MCP tool catalog. Full private transcripts and unrelated conversations are not published.

## Strata PR #4166: not rejected

The [linked job](https://github.com/Niko1221/Strata/actions/runs/40240917297/job/121312294553) is **sweep: skipped**. The [Intake run](https://github.com/Niko1221/Strata/actions/runs/40240917297) concluded **{audit['runConclusion']}** and its `check` job passed. The [workflow]({audit['workflowUrl']}) permits `sweep` only for scheduled or manually dispatched events; this run was triggered by `pull_request_target`.

At the recorded check, [PR #4166]({audit['prUrl']}) was **{audit['prState']}**, merged={audit['merged']}, with no rejection review or review comments. GitHub returned mergeableState={audit['mergeableState']}; that does not establish a rejection or acceptance. No upstream workflow was changed or unnecessary rerun requested. The official benchmark measurements remain awaiting maintainer review.

## Reproduce and inspect

1. Review `plan.json`, the source fixtures, frozen graders and their SHA256 hashes.
2. In an existing PrimeAgent setup, run `Prepare-PrimeAgentExtended.py` to create a fresh isolated workspace and plan. It does not install software or switch the model.
3. Run `node --use-system-ca Run-PrimeAgentQuality.cjs --plan <fresh-plan.json>` with the installed Qwen Playwright runtime and Edge.
4. Run `python Grade-PrimeAgentExtended.py <result-directory>` and `node Grade-PrimeAgentSudoku.cjs <result-directory>` to evaluate the generated outputs. Grade scripts are not supplied to the agent during its tasks.
5. Inspect `browser-summary.json`, the independent JSON reports, generated code, screenshots and the generated HTML. A successful native portal HTML download was not obtained. LAN conversation URLs require access to AIPC. Browser automation currently uses the installed Windows paths on AIPC; other machines must supply their corresponding Edge and Qwen Playwright paths.

[Download the generated Sudoku](PrimeAgent-Sudoku.html?raw=true) · [All campaign results](../../ALL_BENCHMARKS.md).
'''
(package/'README.md').write_text(text,encoding='utf-8',newline='\n')
(directory/'RESULTS.md').write_text(text,encoding='utf-8',newline='\n')
labels={'repair':'Python decimal-invoice code repair','sql':'SQLite multi-table financial report','sudoku':'Playable Sudoku: browser, download and phone layout','evidence':'Conflicting Arabic approved/draft evidence'}
inventory=root/'ALL_BENCHMARKS.md';inventory_text=inventory.read_text(encoding='utf-8-sig')
marker='| New CSV coding task through browser |'
new_rows='\n'.join(f"| Extended: {labels[task]} | **{info['passed']}/{info['checks']}** independent checks passed | [Extended public package](https://github.com/AsaadAlSharif/local-llm-benchmarks/tree/main/primeagent/20261026-extended) |" for task,info in aggregate.items())
if '| Extended: Python decimal-invoice code repair |' not in inventory_text:inventory_text=inventory_text.replace(marker,new_rows+'\n'+marker)
if '## Strata submission status audit' not in inventory_text:
    inventory_text+='\n## Strata submission status audit\n\nOn October 26, 2026, PR #4166 was open and unmerged with no submitted reviews. The linked Intake run succeeded; its `check` job passed and `sweep` was intentionally skipped because it only runs for scheduled/manual events. No rejection was found. [Audit evidence](primeagent/20261026-extended/strata-pr-audit.json). No upstream workflow change was needed.\n'
inventory.write_text(inventory_text,encoding='utf-8',newline='\n')
(publication/'ALL_BENCHMARKS.md').write_text(inventory_text,encoding='utf-8',newline='\n')
readme=publication/'README.md';readme_text=readme.read_text(encoding='utf-8-sig')
start='<!-- primeagent-extended-start -->';end='<!-- primeagent-extended-end -->'
extended=start+'\n## Four additional PrimeAgent tasks\n\n'+'\n'.join(f"- **{labels[task]}:** {info['passed']}/{info['checks']} independent checks passed." for task,info in aggregate.items())+'\n\n[Complete extended evidence, generated code, screenshots and failures](primeagent/20261026-extended). Tests ran through the actual chat UI. Graders were frozen beforehand; self-corrections and failed attempts are retained. These are custom functional tests, not a global ranking.\n\nThe [Strata PR](https://github.com/Niko1221/Strata/pull/4166) has **not been rejected**: Intake passed and the scheduled-only sweep job was skipped. Maintainer review is still pending.\n'+end+'\n\n'
if start in readme_text:
    before,rest=readme_text.split(start,1);rest=rest.split(end,1)[1].lstrip('\n');readme_text=before+extended+rest
else:
    anchor='**[Complete benchmark and test inventory]';readme_text=readme_text.replace(anchor,extended+anchor,1)
readme_text=readme_text.replace('The latest custom functional evaluation used','The earlier custom functional evaluation used')
readme.write_text(readme_text,encoding='utf-8',newline='\n')
manifest={str(p.relative_to(package)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(package.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'}
write_json('SHA256SUMS.json',manifest)
print(json.dumps({'package':str(package),'files':len(manifest),'results':aggregate},ensure_ascii=True))
