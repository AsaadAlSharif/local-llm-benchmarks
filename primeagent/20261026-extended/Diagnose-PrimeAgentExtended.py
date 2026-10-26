"""Post-run diagnosis. Does not change frozen scores or repair agent output."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
directory=Path(sys.argv[1]);load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
plan=load(directory/'plan.json');workspace=Path(plan['workspace'])
expected={'project':'واحة المعرفة','supplier':'شركة النور','currency':'AED','currentDate':'2026-02-28','previousDate':'2026-01-31','currentSource':'02-approved.docx','previousSource':'01-approved.docx','excludedSources':['03-draft.docx'],'currentTotal':2500,'previousTotal':2000,'delta':500,'percentIncrease':25}
misplaced=workspace/'result.json';actual=load(misplaced)
browser=load(directory/'browser-verification.json');a=next(a for a in browser['attempts'] if a['task']=='evidence')
facts={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'kind':'supplementary post-run diagnosis, not a replacement benchmark score','expectedPathExists':(workspace/'evidence/result.json').exists(),'actualMisplacedPath':str(misplaced),'schemaMatches':set(actual)==set(expected),'fieldMatches':{k:actual.get(k)==v for k,v in expected.items()},'documentReadsCompleted':sum(t['tool']=='mcp__local-workbench__read_document' and t['status']=='completed' for t in a['tools']),'mathCallsCompleted':sum(t['tool']=='mcp__local-workbench__math_compute' and t['status']=='completed' for t in a['tools']),'originalDocumentsUnchanged':all(p.read_bytes()==(workspace/'evidence'/p.name).read_bytes() for p in (directory/'inputs/evidence').glob('*.docx')),'artifactObservation':'Native html artifact opens as a playable preview. No Download control was visible in the conversation, environment panel or opened artifact panel. A direct server fetch was not substituted for a user Download action.','sessionObservation':'Sudoku original turn finished and its own background servers were stopped. Native hasTurnError remained true; exact cause not established. The first observer stopped early while the turn was active. Re-observation used the same session and no new prompt. Full transcript pagination was added.','frozenGraderUnmodified':True}
(directory/'post-run-diagnosis.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
print(json.dumps(facts,ensure_ascii=True))
