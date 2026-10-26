# Local LLM benchmark results

Measurements and submissions by **Asaad AlSharif**. Model and engine authors retain their original credits; these results do not claim authorship of Qwen or Strata.

This repository preserves measured results, official runner outputs and reproduction settings. Each model variant and benchmark suite is a separate result. Interrupted attempts are documented locally and excluded from reported scores. A completed local run, a public upload and accepted leaderboard inclusion are separate states.

## Published results

| Benchmark | Model | Generation speed | Quality score | Public result |
|---|---|---:|---:|---|
| llm-bench.io, client 0.4.98+102 | Qwen3.8 Flash-Next Coder IQ1_M | 172.3 tok/s | 80.8 / 100 | [Official result](https://llm-bench.io/benchmarks/cmvp6e3so000u01la94ncayf7) |

The Coder result is a complete four-scenario run. Its site-reported breakdown is agent workflow 79.4, coding 62.0, roleplay 93.7 and research 88.1. Prompt processing is 2,163.4 tok/s and average first-token latency is 195 ms. These are the platform's metrics and LLM-judge scores; the coding score is not a unit-test pass rate.

## Reproduction

- Hardware reported by the client: NVIDIA GeForce RTX 5090, AMD Ryzen 9 9950X, Windows 11 Pro for Workstations 26H2. Keep the hardware report with each individual result.
- Actual installed engine for the Coder run: **Strata CLI 0.2.5 / engine 0.1.50**. The official client's manual-endpoint path displays `Strata (manual)` on the public page despite being supplied the measured version. The local run record preserves the actual version separately; no score was edited to compensate.
- Coder used the source-advertised **131,072-token** context, source-default sampling (temperature 1, top-p 0.95, top-k 20) and source-default thinking effort (`xhigh`). Native image input was enabled and the native server exposed four slots.
- Benchmarks run sequentially. The local speed-run launcher waits for an idle model and aborts its own client if another active inference is observed. It never cancels a user's chat.
- Model files: [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF). Coder first shard SHA-256: `e11083ba855e7666b48ea3f2db6a9c3a20c18751a012cc24f948de91b7087fad`.

## Scope

OpenClaw-based suites are excluded. The local runners do not call Google model/services, run Google's MBPP dataset or run Google's IFEval benchmark. Independent boards may list Google competitors. HumanEval+ preparation uses the unchanged EvalPlus OpenAI-compatible adapter and scorer, with Google SDK dependencies omitted; preparation is not a completed quality score.

Every suite retains its own protocol and dataset version. Scores from different suites are not interchangeable. Comparisons between saved Strata profiles must account for image-input and slot settings; they are not automatically a controlled quantization-only experiment.

## Excluded submission

The earlier [Q2_0 submission cmvp6wrdy001101lakkk002k8](https://llm-bench.io/benchmarks/cmvp6wrdy001101lakkk002k8) is excluded. An extra device-fingerprint registration prompt shifted the initial automation's positional menu input. It uploaded an 8,192-token context label while the native runtime and intended benchmark context were 131,072. Do not use that entry in this comparison. The local withdrawal request returned HTTP 403; the site has not removed it. The corrected runner matches each actual prompt and records its source-derived answer before executing another benchmark.
