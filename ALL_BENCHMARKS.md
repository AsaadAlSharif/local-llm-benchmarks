# Complete benchmark and test inventory

Asaad AlSharif / PrimeAgent project. Updated October 26, 2026. This covers the measurements and acceptance checks for this Strata/PrimeAgent campaign. Other contributors' reports in the cloned repository are not our measurements. A model benchmark, an agent functional check and a leaderboard acceptance are different results.

## Completed performance/quality suites

| Suite | Model / configuration | Actual result | Public evidence / status |
|---|---|---|---|
| Official Strata draft standard, fresh engine | Q2_0 | 21 measured requests; **12/12** sanity checks; short/4K/16K decode medians **270.7 / 258.0 / 220.4 tok/s** | [Native report](https://github.com/AsaadAlSharif/Strata/tree/benchmark/asaad-rtx5090-q2-iq3s-20261026/bench/results/2026-10-25-community-rtx-5090-9950x-asaad-q2-iq3s/standard-q2-0), [PR #4166](https://github.com/Niko1221/Strata/pull/4166), awaiting review |
| Official Strata draft standard, fresh engine | IQ3_S | 21 measured requests; **12/12** sanity checks; short/4K/16K decode medians **219.5 / 195.0 / 208.9 tok/s** | [Native report](https://github.com/AsaadAlSharif/Strata/tree/benchmark/asaad-rtx5090-q2-iq3s-20261026/bench/results/2026-10-25-community-rtx-5090-9950x-asaad-q2-iq3s/standard-iq3-s), same public PR |
| Earlier Strata draft standard | Q2_0, one readiness request before suite | **12/12** sanity checks; medians **264.0 / 261.5 / 250.1 tok/s**; not a fresh-engine run | [Historical report](https://github.com/AsaadAlSharif/Strata/tree/benchmark/asaad-rtx5090-q2-iq3s-20261026/bench/results/2026-10-25-community-rtx-5090-9950x-asaad-q2-iq3s/historical-standard-q2-0), excluded from the fresh comparison |
| Earlier Strata greedy quick suite | Q2_0, thinking off, temperature zero | Short-chat median **245.0 tok/s**; 32K prompt median **7520.9 prompt tok/s**; not a full quality test | [Historical report](https://github.com/AsaadAlSharif/Strata/tree/benchmark/asaad-rtx5090-q2-iq3s-20261026/bench/results/2026-10-25-community-rtx-5090-9950x-asaad-q2-iq3s/historical-greedy-q2-0) |
| llm-bench.io, four scenarios | Coder IQ1_M | **172.3 tok/s; 80.8/100** overall judge score | [Public result](https://llm-bench.io/benchmarks/cmvp6e3so000u01la94ncayf7) |
| llm-bench.io, four scenarios | Q2_0 corrected | **226.6 tok/s; 83.4/100** | [Public result](https://llm-bench.io/benchmarks/cmvp78gin001901lappq748vm) |
| llm-bench.io, four scenarios | IQ3_S | **190.3 tok/s; 88.4/100** | [Public result](https://llm-bench.io/benchmarks/cmvp7iusf002101la2fljy8q2) |

The Strata protocol is a draft, with nine performance requests and twelve sanity requests plus an excluded warm-up per fresh suite. Truncated throughput outputs remain in the reports. These small sanity checks are not full coding or agent scores. llm-bench scores are model-judge scores and use different profiles; they are not interchangeable with Strata or execution-test scores. The llm-bench uploads preceded the stricter Google-board exclusion and remain outside the current campaign scope. No new speed run was made in the latest PrimeAgent test.

## PrimeAgent actual-agent checks

| Test | Actual result | Evidence |
|---|---|---|
| New CSV coding task through browser | Agent's own **53** tests passed; independent **546/546** checks passed; initial shell denial recovered | [Fresh public package](https://github.com/AsaadAlSharif/local-llm-benchmarks/tree/main/primeagent/20261026-quality) |
| First Arabic document attempt | **Blocked** by stale MCP read roots; no fabricated JSON; presentation dependency blocked | Same package, original-browser-summary.json |
| After workspace fix | Document and presentation succeeded; eight math and one filename retries retained | Same package, workspace-fix-browser-summary.json |
| Final fresh document/artifact tasks | **23/23** independent checks; zero failed tool calls; actual two-slide PowerPoint downloaded | Same package, final-tool-contract-fix-browser-summary.json |
| Earlier Coder setup acceptance | Real browser coding/shell/MCP task; independent **5177** cases passed | Locally re-inspected runtime/coder-iq1-m/RESULTS.md and independent-code-verification.json; [LAN conversation](https://aipc/session/e7242cf3-ef82-4c2b-b5fe-949147495e8a) |
| Earlier Coder CLI and UI connection checks | CODER_CLI_OK; all three MCP connections; browser exact math 1591 | Same local setup evidence; [LAN final conversation](https://aipc/session/659a5c54-00f7-45a1-9ece-ce3fa3de8cc8) |
| Earlier workspace cutover task | Actual MCP math 391, file write/read and browser Download byte equality | runtime/workspace-cutover/20261026-015556/browser-verification.json; [LAN conversation](https://aipc/session/2ce9af60-f1e5-4474-a452-77a6c796249b) |
| Earlier Strata/API portal acceptance | Native model selection, MCP math, artifact download, normal-chat image 639 and five source-discovery checks | Locally re-inspected runtime/strata-api-acceptance/RESULTS.md; integration checks, not a full benchmark |
| Earlier autonomous-question workflow | Full Access, manual answer priority and automatic recommendations after 45 seconds, including browser closed | runtime/autonomy-acceptance/RESULTS.md and verification.json; integration checks, not a model score |
| Earlier local-workbench verification | Saved library/MCP verification and actual portal math 403 + web-search calls | tools/data/verification.json and qwen-verification.json; historical integration checks |

LAN links require access to AIPC. Local-only historical receipts have not all been republished; their paths identify the original evidence. The new functional package is publicly downloadable and contains no unrelated chat histories. Historical timing observations are not promoted to controlled performance improvements. No pass of the entire global MCP catalog is claimed.

## Incomplete, invalid or excluded attempts

| Attempt | Outcome |
|---|---|
| First two llm-bench Coder attempts | Interrupted for concurrent browser inference; no complete result or upload |
| First completed Q2_0 llm-bench upload | [Incorrect context label](https://llm-bench.io/benchmarks/cmvp6wrdy001101lakkk002k8), excluded; withdrawal request returned 403; corrected run separate |
| Initial capped HumanEval setup | Stopped after ten saved answers; no full evaluation or submitted score |
| Native-budget HumanEval+ | 145/164 recorded answers; stopped after user excluded boards listing Gemini; **no final score or submission** |
| Original PrimeAgent document/presentation tasks | Blocked by the now-fixed workspace mismatch; preserved separately from post-fix success |

Not run/submitted: PinchBench, LiveBench, Aider Polyglot, SWE-bench, LiveCodeBench and Terminal-Bench. Exclusions/eligibility holds remain in the campaign record. Earlier browser first-response latency of 83.788 seconds is preserved in the Strata historical report; it was an operational observation, not a benchmark distribution. No global rank has been established.
