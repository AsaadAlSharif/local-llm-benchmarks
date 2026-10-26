# PrimeAgent benchmark and test reports

Measurements and submissions by **Asaad AlSharif**. Model and engine authors retain their original credits; these results do not claim authorship of Qwen or Strata.

**[Complete benchmark and test inventory](ALL_BENCHMARKS.md)** includes the official Strata suites, historical/partial attempts, llm-bench.io results and actual PrimeAgent user-interface tests.

## PrimeAgent tested through its real chat interface

The latest custom functional evaluation used the normal HTTPS browser composer, Coder IQ1_M, deferred MCP discovery, actual tool execution and the artifact Download button. The original blocked document workflow and intermediate retries are retained alongside the corrected result.

| Check | Result |
|---|---|
| Generated CSV parser | **546/546** independent checks passed; agent's own 53 tests also passed |
| Arabic document, exact money calculations and PowerPoint download | **23/23** independent checks passed |
| Final fresh document/presentation tasks | **Zero failed tool calls; zero browser errors** |
| Delivered presentation | Two slides; PrimeAgent / Asaad AlSharif attribution; correct 560.18 AED total |

[Full functional-test evidence and reproduction](primeagent/20261026-quality) · [Download the verified PowerPoint](primeagent/20261026-quality/PrimeAgent-Asaad-AlSharif.pptx?raw=true).

This is a custom agent evaluation. It does not establish a global rank or a standardized model-benchmark score. The fix makes MCP document access and output delivery follow the portal's configured workspaces dynamically. No new speed benchmark was run.

## Official Strata draft-standard submissions

| Model | Measured requests | Sanity checks | Short / 4K / 16K decode medians |
|---|---:|---:|---|
| Q2_0 | 21 plus excluded warm-up | 12/12 | 270.7 / 258.0 / 220.4 tok/s |
| IQ3_S | 21 plus excluded warm-up | 12/12 | 219.5 / 195.0 / 208.9 tok/s |

[Public Strata PR #4166](https://github.com/Niko1221/Strata/pull/4166), awaiting maintainer review. The native draft protocol and its small sanity checks are separate from the PrimeAgent functional tests above.

This repository preserves measured results, official runner outputs and reproduction settings. Each model variant and benchmark suite is a separate result. Interrupted attempts are documented locally and excluded from reported scores. A completed local run, a public upload and accepted leaderboard inclusion are separate states.

## Campaign scope updated October 26, 2026

The benchmark operator clarified that independent boards listing Gemini must also be excluded, in addition to Google tools/models/services/datasets and OpenClaw. Speed benchmarking is deferred to keep normal chat available. No further submissions will be made to excluded boards. The three llm-bench.io uploads below preceded this clarification; they remain historical public measurements outside the current campaign scope. They have not been withdrawn. llm-bench.io lists [Google Gemma](https://llm-bench.io/models/gemma-4-e2b).

The HumanEval+ generation was stopped at 145 of 164 recorded answers after the clarification, because EvalPlus's [official leaderboard data lists Gemini](https://raw.githubusercontent.com/evalplus/evalplus.github.io/master/results.json). It was not scored or submitted, and no partial pass rate is claimed. Benchmark jobs have stopped; the Coder model remains available for ordinary chat.

## Historical uploads before the stricter clarification

| Benchmark | Model | Generation speed | Quality score | Public result |
|---|---|---:|---:|---|
| llm-bench.io, client 0.4.98+102 | Qwen3.8 Flash-Next Coder IQ1_M | 172.3 tok/s | 80.8 / 100 | [Official result](https://llm-bench.io/benchmarks/cmvp6e3so000u01la94ncayf7) |
| llm-bench.io, client 0.4.98+102 | Qwen3.8 Flash-Next Q2_0 | 226.6 tok/s | 83.4 / 100 | [Official result](https://llm-bench.io/benchmarks/cmvp78gin001901lappq748vm) |
| llm-bench.io, client 0.4.98+102 | Qwen3.8 Flash-Next IQ3_S | 190.3 tok/s | 88.4 / 100 | [Official result](https://llm-bench.io/benchmarks/cmvp7iusf002101la2fljy8q2) |

The Coder result is a complete four-scenario run. Its site-reported breakdown is agent workflow 79.4, coding 62.0, roleplay 93.7 and research 88.1. Prompt processing is 2,163.4 tok/s and average first-token latency is 195 ms. These are the platform's metrics and LLM-judge scores; the coding score is not a unit-test pass rate.

## Reproduction

- Hardware reported by the client: NVIDIA GeForce RTX 5090, AMD Ryzen 9 9950X, Windows 11 Pro for Workstations 26H2. Keep the hardware report with each individual result.
- Actual installed engine for the Coder run: **Strata CLI 0.2.5 / engine 0.1.50**. The official client's manual-endpoint path displays `Strata (manual)` on the public page despite being supplied the measured version. The local run record preserves the actual version separately; no score was edited to compensate.
- Coder used the source-advertised **131,072-token** context, source-default sampling (temperature 1, top-p 0.95, top-k 20) and source-default thinking effort (`xhigh`). Native image input was enabled and the native server exposed four slots.
- The corrected Q2_0 run also used 131,072 tokens and source-default sampling/thinking. Its existing saved native profile had image input disabled and one slot. The site reports agent workflow 81.3, coding 77.2, roleplay 90.9 and research 84.1, with average first-token latency 108 ms. The profile difference means this is not an isolated quantization-only comparison against Coder.
- IQ3_S used 131,072 tokens, source-default sampling/thinking, image input enabled and one slot. The site reports agent workflow 93.9, coding 75.9, roleplay 95.2 and research 88.8, prompt processing 1,282.6 tok/s and average first-token latency 491 ms.
- Benchmarks run sequentially. The local speed-run launcher waits for an idle model and aborts its own client if another active inference is observed. It never cancels a user's chat.
- Model files: [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF). Coder first shard SHA-256: `e11083ba855e7666b48ea3f2db6a9c3a20c18751a012cc24f948de91b7087fad`.

## Scope

OpenClaw-based suites, Google tools/models/services/datasets and independent boards listing Gemini are excluded. A board must pass this scope review before any future run or submission. Speed benchmarks are deferred. Partial HumanEval outputs remain local and are not a complete quality result. No Google SDK was installed for that attempt and no MBPP or IFEval tasks were run.

Every suite retains its own protocol and dataset version. Scores from different suites are not interchangeable. Comparisons between saved Strata profiles must account for image-input and slot settings; they are not automatically a controlled quantization-only experiment.

## Excluded submission

The earlier [Q2_0 submission cmvp6wrdy001101lakkk002k8](https://llm-bench.io/benchmarks/cmvp6wrdy001101lakkk002k8) is excluded. An extra device-fingerprint registration prompt shifted the initial automation's positional menu input. It uploaded an 8,192-token context label while the native runtime and intended benchmark context were 131,072. Do not use that entry in this comparison. The local withdrawal request returned HTTP 403; the site has not removed it. The corrected runner matches each actual prompt and records its source-derived answer before executing another benchmark.
