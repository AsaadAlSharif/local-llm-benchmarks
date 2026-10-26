# PrimeAgent extended functional evaluation

**Asaad AlSharif — PrimeAgent**, October 26, 2026.

Four new tasks were submitted through the normal HTTPS chat composer, using **qwen3.8-flash-next-coder-iq1_m** with its existing model settings. Inputs and independent grader hashes were frozen before the first task. These are custom functional evaluations, not a standardized leaderboard or a global rank. No speed benchmark, model switch, excluded-board run or default-setting change was made. Normal chat stayed available.

| Task | Independent checks passed | Failed tool-status events | Actual user-interface evidence |
|---|---:|---:|---|
| repair | 54/54 | 0 | [LAN conversation](https://aipc/session/cb481a59-1e50-4c32-9b3f-da4149bd7bc7) |
| sql | 11/11 | 2 | [LAN conversation](https://aipc/session/9a3d43dd-21cf-4927-9c16-025327677332) |
| sudoku | 18/21 | 10 | [LAN conversation](https://aipc/session/38bc6611-0960-4220-9015-ea3b82f4bcbb) |
| evidence | 1/2 | 0 | [LAN conversation](https://aipc/session/361e95fd-3f30-4cbe-96d0-24dbc8089eee) |

The tasks test decimal rounding/validation and code repair; SQLite join fan-out, invoice statuses and per-invoice overpayments; a real Sudoku browser interaction including incomplete/invalid board checks, solving, keyboard and phone layout; and conflicting Arabic documents where the latest draft must be excluded from approved totals. Check counts represent different assertions, not independent benchmark questions or comparable model scores. A completed shell-tool event is not by itself proof that its command succeeded; independent output checks determine the result.

## Failures and limits

- sudoku: UI turn completed without browser/observer/turn errors: UI turn completed without browser/observer/turn errors
- sudoku: Browser Download matches generated file byte for byte: ENOENT: no such file or directory, open 'D:\AI\Agent\Qwen Code\qwen-web\benchmarks\primeagent-extended\20261026-144451\downloaded-sudoku.html'
- sudoku: Zero is rejected: Expected values to be strictly equal:

'0' !== ''

- evidence: Load evidence result: [Errno 2] No such file or directory: 'D:\\AI\\Agent\\Workspace\\primeagent-extended-20261026-144451\\evidence\\result.json'

The first automation launch stopped before any model request because Node did not use the installed local certificate authority. That observer failure is retained in `observer-certificate-attempt.json`; retry used Node's `--use-system-ca` and preserved certificate validation. There was one initial agent turn per task. Self-corrections within that turn are retained in the tool-event summaries. Codex did not repair the generated implementations or feed grader failures back to the model.

The first Sudoku observer also stopped early on a native error flag while the agent continued working. Its premature grader reports are retained but superseded by the final unchanged graders, run after the original turn completed. Observation was corrected to consider active/background state and to page the full transcript. The Arabic task briefly overlapped the tail of Sudoku because of that observer error; no timing or controlled speed claim is made. No additional agent request was sent to improve the Sudoku result.

**Diagnosis:** The repair and SQL tasks passed their frozen independent checks. Sudoku passed 18 of 19 game/browser checks, but pasted `0` remained in a cell. Its native artifact was registered and opened as a playable HTML preview; no Download control was available in the conversation, environment panel or opened artifact panel, so portal Download/byte equality did not pass. Native session status still reported `hasTurnError=true` after the agent finished and stopped its test servers; its exact cause is not established. The public Sudoku below is copied from the generated file, not claimed as a portal download.

The Arabic task read all three sources and made four successful math calls. Its result has the correct schema and all twelve values, but it wrote `result.json` in the test root instead of `evidence/result.json`. The required-path check therefore failed and dependent field checks in the frozen grader were not executed. `post-run-diagnosis.json` and `generated/misplaced-evidence-result.json` preserve the separate content verification without converting this delivery failure into a pass. The source DOCX files were unchanged.

Arabic evidence uses locally generated DOCX text, not scanned-PDF OCR. Sudoku uses one fixed starting puzzle; random generation/difficulty calibration are not tested. These results do not cover the entire MCP tool catalog. Full private transcripts and unrelated conversations are not published.

## Strata PR #4166: not rejected

The [linked job](https://github.com/Niko1221/Strata/actions/runs/40240917297/job/121312294553) is **sweep: skipped**. The [Intake run](https://github.com/Niko1221/Strata/actions/runs/40240917297) concluded **success** and its `check` job passed. The [workflow](https://github.com/Niko1221/Strata/blob/4b9e05a2a806a3fe24f7b2560d98626c37dade35/.github/workflows/intake.yml) permits `sweep` only for scheduled or manually dispatched events; this run was triggered by `pull_request_target`.

At the recorded check, [PR #4166](https://github.com/Niko1221/Strata/pull/4166) was **open**, merged=False, with no rejection review or review comments. GitHub returned mergeableState=unstable; that does not establish a rejection or acceptance. No upstream workflow was changed or unnecessary rerun requested. The official benchmark measurements remain awaiting maintainer review.

## Reproduce and inspect

1. Review `plan.json`, the source fixtures, frozen graders and their SHA256 hashes.
2. In an existing PrimeAgent setup, run `Prepare-PrimeAgentExtended.py` to create a fresh isolated workspace and plan. It does not install software or switch the model.
3. Run `node --use-system-ca Run-PrimeAgentQuality.cjs --plan <fresh-plan.json>` with the installed Qwen Playwright runtime and Edge.
4. Run `python Grade-PrimeAgentExtended.py <result-directory>` and `node Grade-PrimeAgentSudoku.cjs <result-directory>` to evaluate the generated outputs. Grade scripts are not supplied to the agent during its tasks.
5. Inspect `browser-summary.json`, the independent JSON reports, generated code, screenshots and the generated HTML. A successful native portal HTML download was not obtained. LAN conversation URLs require access to AIPC. Browser automation currently uses the installed Windows paths on AIPC; other machines must supply their corresponding Edge and Qwen Playwright paths.

[Download the generated Sudoku](PrimeAgent-Sudoku.html?raw=true) · [All campaign results](../../ALL_BENCHMARKS.md).
