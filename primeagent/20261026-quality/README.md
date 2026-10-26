# PrimeAgent functional evaluation - Asaad AlSharif

Actual user-interface evaluation on October 26, 2026. PrimeAgent used `qwen3.8-flash-next-coder-iq1_m` through its existing Strata endpoint, source context 131,072. These are custom functional checks, not a standardized leaderboard result or a global ranking. No inference settings, model or token limit were changed; speed testing remained deferred and ordinary chat stayed available.

| Task | Independent result | Actual user path |
|---|---|---|
| CSV parser implementation | **546/546** checks passed, including 512 serialized round trips | HTTPS New task, native file tools and real Node execution |
| Arabic invoice and exact VAT | All source fields and amounts correct: subtotal 533.50, VAT 26.68, total **560.18 AED** | Deferred MCP discovery, actual document reader, exact-math calls, JSON write/read |
| PowerPoint delivery | **2 slides**, correct Arabic supplier and amounts, **29,559 downloaded bytes** | Presentation MCP, native record_artifact, actual browser Download button |
| Combined document/artifact verification | **23/23** passed | Includes downloaded/native byte equality and OOXML/content inspection |

## Original failures and fixes

The first coding attempt contained one shell-guard denial. The agent recovered with native file discovery and ran its own tests (53 passing); independent grading then passed 546 checks. The generated code was not repaired by the benchmark operator.

The first document attempt was **blocked**: the agent workspace had moved, but MCP read_roots retained the earlier paths. The agent did not invent the invoice values. The dependent presentation task was blocked and was not counted as passing. Both original outcomes are retained.

The shared tool configuration now reads primary/additional workspaces dynamically from portal.config.json on every call. Removed inherited roots stop being readable; explicit read roots and private-file/resolved-path checks remain. New documents default to the current configured primary workspace/output, allowing native artifact registration. Additional configured workspaces can select an absolute output name inside their own output directory. Existing files remain protected against overwrite.

After the workspace fix, the document/artifact checks passed, but the agent made eight rejected math calls and one rejected presentation call before recovery. The math contract now supports constrained exact Rational and floor/ceiling expressions and explains that decimal literals are already exact. Missing document filename extensions are added by the shared output helper. No arbitrary Python execution was enabled.

Fresh document/presentation tasks after those changes completed with **zero failed tool calls, zero turn errors and zero browser page errors**. The first blocked run and intermediate retries are separately retained in the browser summaries. Ten focused workspace checks and eleven tool-contract checks passed. Outputs from the blocked run were not invented or relabeled as success.

## Evidence and reproduction

- Original/final plans contain the exact prompts and rubric. Synthetic invoice DOCX, expected JSON, actual JSON, generated parser/tests, independent graders, current tool source, compact tool-status traces and screenshots are included.
- Full private transcripts remain local. Public screenshots crop out unrelated session titles; unrelated chat content and credentials are not included. Only local installation-root strings in JSON are replaced by placeholders. Numeric measurements, answers and statuses are unchanged.
- Session URLs in JSON are **LAN-only** AIPC links; external readers use this public package. To reproduce, place the runner/preparation/graders and campaign-policy.json under your configured portal's benchmarks directory, adjust the installed Qwen Playwright/Edge paths and AIPC host for your machine, prepare fresh inputs, submit through the normal composer, then run the independent graders. The scripts use the existing parent portal.config.json; they do not create a replacement agent service.
- This is a small functional evaluation with a synthetic invoice and one coding task. It does not measure full agent reliability, energy efficiency, controlled throughput, every MCP tool, desktop PowerPoint rendering or a global number-one rank. Original coding was not rerun because subsequent changes affected the document tools; the final two tasks used fresh inputs/output names.

[Download the verified PowerPoint](PrimeAgent-Asaad-AlSharif.pptx?raw=true). File SHA-256: `bc60cb3b89215e6ebdadf15d15bb5eb81aaeab0ce1b662aac51b7a0224121ffe`.
