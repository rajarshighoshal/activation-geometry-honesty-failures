# Artifact Guide

This repository is a public artifact record for activation-space experiments on honesty
failures in language models. It currently contains two cleaned results:

1. a paired synthetic-pressure activation-monitoring pilot;
2. a graded PASS/FAIL control audit showing why directional steering results must be
   split by error type.

## Scope

The synthetic-pressure artifact includes:

- generated paired pressure/neutral scenario specs;
- retained Llama-3.1-8B-Instruct rollout transcripts;
- Opus 4.8 and DeepSeek v4 Pro stance labels;
- pair-grouped per-turn and trajectory evaluation JSONs;
- bootstrap confidence intervals for the headline metrics;
- scripts to regenerate summaries and figures from the committed artifacts;
- tests for the evaluation and summarization code.

The graded-control audit includes:

- a public result note at `docs/graded_control_directional_audit.md`;
- public figures under `figures/graded_control/`;
- a sanitized summary JSON at `results/eval/graded_control/directional_audit_summary.json`.

This artifact does **not** include:

- model weights;
- large activation tensors/checkpoints;
- the broader private research branch or work-in-progress local scripts;
- claims that geometry-aware probes beat Euclidean baselines.

## Claims Supported by This Artifact

Supported:

1. Pressure-induced acceptance of a false premise is strongly decodable from
   mid-layer residual-stream activations in this retained pilot.
2. Conversation-level trajectory summaries have higher point estimates than per-turn
   probes for flip-vs-steadfast-correct classification.
3. The trajectory gain and geometry-vs-Euclidean gap are not statistically separated
   at this pilot size.
4. Tangent-subspace geometry-aware probes are competitive but do not clearly beat
   simple Euclidean linear/MLP baselines.
5. In the graded-control audit, mean-difference/tangent steering does not establish
   bidirectional truth restoration; the corrected oracle test fails in the
   `false_PASS -> FAIL` direction.
6. Aggregate steering metrics can hide one-way label pushing and should be reported by
   error direction.

Not supported:

1. Non-Euclidean geometry is necessary for detecting caving.
2. The probed directions causally control the model.
3. The result generalizes to all models or natural sycophancy settings.
4. The current tangent steering method controls deception.

## Reproduce the Public Figures

From the repository root:

```bash
python3 experiments/summarize_synthetic_pressure.py
python3 experiments/plot_summary.py
```

Expected outputs:

- `results/eval/synthetic_pressure_llama8b/final_summary.json`
- `results/eval/synthetic_pressure_llama8b/final_summary.md`
- `figures/dataset_filter.svg`
- `figures/per_turn_auroc.svg`
- `figures/headline_ci.svg`

The summary is rebuilt from committed JSON artifacts; no GPU or API keys are needed
for this path.

## Run Tests

```bash
pip install -e ".[dev]"
python3 -m pytest -q
```

Expected result at the current artifact snapshot: 28 tests pass.

## Full Pipeline From Scratch

The full pipeline is documented in the README. It requires:

- GPU access for model rollout and activation capture;
- access to gated Llama-3.1-8B-Instruct weights;
- Anthropic and DeepSeek-compatible API access for scenario generation and judging.

For artifact review, the recommended path is to inspect the committed data/results and
rerun the no-GPU summary/plot/test commands above.

## Key Result Files

| File | Purpose |
| --- | --- |
| `results/eval/synthetic_pressure_llama8b/final_summary.json` | canonical headline summary |
| `results/eval/synthetic_pressure_llama8b/bootstrap_ci.json` | clustered bootstrap intervals |
| `results/eval/synthetic_pressure_llama8b/per_turn_probes_opus_pairgroup.json` | per-turn Opus-label probes |
| `results/eval/synthetic_pressure_llama8b/per_turn_probes_deepseek_pairgroup.json` | per-turn DeepSeek-label probes |
| `results/eval/synthetic_pressure_llama8b/trajectory_baselines_opus_pairgroup.json` | trajectory Opus-label probes |
| `results/eval/synthetic_pressure_llama8b/trajectory_baselines_deepseek_pairgroup.json` | trajectory DeepSeek-label probes |

## Methodological Guardrails

- Cross-validation is grouped by paired scenario, not by individual turn.
- The pressured and neutral arms of the same scenario never cross train/test folds in
  the final reported files.
- Bootstrap intervals resample paired scenarios, not individual turns.
- The knowledge-check filter is explicit: only cases where the model knew the premise
  was false before pressure are kept.
