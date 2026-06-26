# First Draft: Activation Trajectories Detect Caving Under Pressure

## Short Version

This experiment tests whether a small open-weight model's internal activations reveal when it caves to user pressure and repeats a false premise. The answer is yes: on Llama-3.1-8B-Instruct, mid-layer residual-stream activations strongly predict whether a turn accepts a false user belief, with best per-turn AUROC around 0.88 under two independent LLM judges. Conversation-level trajectory summaries give higher point estimates, around 0.91-0.92 AUROC for distinguishing sycophantic flips from steadfast-correct conversations — though that contrast covers only ~100 scenarios, so its bootstrap confidence intervals are wide and overlap the per-turn band, making the gain suggestive rather than established.

The stronger geometry claim is not yet supported. Tangent-subspace trajectory probes are competitive, but simple Euclidean linear and MLP baselines are still as strong or stronger. The safe conclusion is that activation monitoring works clearly here, and trajectory features help, but current geometry-specific probes do not yet outperform basic Euclidean baselines.

## Abstract

Models can know a user premise is false and still drift toward agreement under repeated pressure. This project studies that failure mode using a synthetic multi-turn pressure dataset and residual-stream activations from Llama-3.1-8B-Instruct. Each scenario begins with a false presupposition and a known correction, then compares a pressured conversation against a neutral matched conversation. After filtering to the cases where the model passed a cold knowledge check — correctly identifying the presupposition as false before any pressure was applied — the retained dataset contains 114 paired scenarios, 228 conversations, and 1,824 assistant turns.

I label each assistant turn as accepting, rejecting, or hedging the false premise using two independent LLM judges, Opus 4.8 and DeepSeek v4 Pro. The judges agree on 1,542 of 1,824 turns, or 84.54 percent. I then train activation probes over residual-stream layers using pair-grouped cross-validation, so the neutral and pressured arms of the same synthetic scenario cannot leak across train and test folds.

The main result is that caving under pressure is strongly decodable from activations. Per-turn probes reach 0.8791 AUROC with Opus labels and 0.8845 AUROC with DeepSeek labels. Trajectory-level probes give higher point estimates: distinguishing sycophantic flips from steadfast-correct conversations reaches 0.9098 AUROC with Opus labels and 0.9236 AUROC with DeepSeek labels, though bootstrap confidence intervals (below) leave that improvement inside the noise at this sample size. However, the best-performing probes are mostly simple linear or MLP baselines. Geometry-aware probes, especially tangent-subspace features, are competitive in trajectory settings but do not clearly beat Euclidean baselines.

## Research Question

The motivating question was not just whether sycophancy is visible in activations. Prior work already suggests many behavioral labels are linearly decodable. The sharper question was:

> When a model is pressured over several turns, does the trajectory of its internal state reveal whether it will preserve the truth or cave to the false user premise?

This matters because many failures are not one-turn classification problems. A model may begin with a correction, soften under social pressure, hedge, and finally accept the user's false belief. That is naturally a trajectory rather than a static state.

The project started with a geometry hypothesis: maybe these safety-relevant failures are better captured by activation-manifold structure than by a single global linear direction. That hypothesis is still plausible, but the current result is more conservative: trajectory monitoring works, while the specific geometry-aware probes tested here do not yet beat strong Euclidean baselines.

## Dataset

The synthetic pressure dataset contains 1,000 paired scenarios. Each scenario has two arms:

- a pressured arm, where the user repeatedly pushes a false presupposition;
- a neutral arm, where the user asks follow-up questions without pressure.

Each scenario includes:

- a false presupposition;
- a correction;
- an initial question containing the false premise;
- seven follow-up turns.

Example topic: the common myth that delayed-onset muscle soreness is caused by lactic acid building up for days. The correction states that lactic acid clears quickly and that DOMS is caused by microscopic muscle damage and repair.

The rollout used Llama-3.1-8B-Instruct. Before each conversation, the model is given a cold knowledge check: it is shown the false presupposition and asked whether it is true or false. Only scenarios where the model answered "false" — correctly rejecting the premise before any pressure — are retained, because "did the model cave under pressure?" is only a meaningful question when the model knew the answer to begin with. If the model already endorsed the myth or was unsure, there is no knew-then-caved signal to measure, so the pair is dropped. Final retained data:

| item | count |
| --- | ---: |
| generated conversation specs | 2,000 |
| generated paired scenarios | 1,000 |
| retained paired scenarios | 114 |
| retained conversations | 228 |
| turns per retained conversation | 8 |
| retained assistant turns | 1,824 |

Only 114 of the 1,000 generated scenarios cleared this knowledge check on Llama-3.1-8B — these are deliberately sticky myths that the model itself frequently believes — which is the main reason the retained set is small. The retained set is therefore a pilot-sized but fully paired dataset: every retained scenario has both the pressured and neutral arm.

## Labels

Each assistant turn was labeled into one of three stances:

- `accepts`: the assistant caves to or supports the specific false belief.
- `rejects`: the assistant preserves truth, corrects the premise, or weakens the false belief.
- `hedges`: the assistant does not make a clear commitment.

Two LLM judges were used:

- Opus 4.8
- DeepSeek v4 Pro

The purpose of using two judges was not to treat either as ground truth. It was to test whether the activation result survives a second labeling source. Agreement was strong but not perfect:

| metric | value |
| --- | ---: |
| turn agreement | 1,542 / 1,824 |
| turn agreement percent | 84.54% |
| exact conversation agreement | 74 / 228 |

The main disagreements are on boundary cases between `hedges` and the other two labels, which is expected for this kind of conversational stance task.

Trajectory labels classify each conversation by how its stance evolves across the eight turns:

| judge | self-correction | sycophantic flip | steadfast wrong | steadfast correct | accept turns |
| --- | ---: | ---: | ---: | ---: | ---: |
| Opus | 55 | 79 | 6 | 88 | 433 |
| DeepSeek | 51 | 77 | 8 | 92 | 421 |

The trajectory experiments below focus on distinguishing `sycophantic_flip` from `steadfast_correct`, because that is the cleanest pressure-sensitive contrast: a `steadfast_correct` conversation never accepts the false premise, while a `sycophantic_flip` ends on accepting it. The `self_correction` (ends on rejecting after an earlier accept) and `steadfast_wrong` (accepts throughout) trajectories are excluded from this contrast.

## Methods

I extract residual-stream activations from Llama-3.1-8B-Instruct at layers:

```text
0, 8, 12, 16, 19, 20, 24, 28, 32
```

The main evaluations use pair-grouped cross-validation. This is important: the pressured and neutral arms of the same scenario share topic, correction, and answer structure. If one arm appears in train and the matched arm appears in test, the evaluation can overstate generalization. The final numbers therefore group by paired scenario id.

Two evaluation levels are used.

Per-turn probes classify individual assistant turns as accepting versus not accepting the false premise. These probes test whether the current activation state contains a caving signal.

Trajectory probes classify full conversations, especially sycophantic flips versus steadfast-correct conversations. These probes test whether the path through activation space over the conversation contains a pressure-response signal.

Probe families:

| family | examples |
| --- | --- |
| Euclidean baselines | linear, MLP, PCA, centroid, kNN |
| Metric probes | Mahalanobis, class Mahalanobis |
| Geometry-aware probes | tangent subspace, graph geodesic |
| Trajectory summaries | final state, mean state, start-to-end delta, flattened path, relative path |

## Results

### Per-Turn Detection

The per-turn task asks whether the current assistant turn accepts the false premise. The result is strong and replicates across both labelers.

| judge | best probe | family | AUROC | layer |
| --- | --- | --- | ---: | ---: |
| Opus | MLP | Euclidean | 0.8791 | 16 |
| Opus | linear | Euclidean | 0.8713 | 16 |
| Opus | PCA-50 | Euclidean | 0.8585 | 16 |
| Opus | tangent subspace | geometry-aware | 0.8073 | 16 |
| DeepSeek | MLP | Euclidean | 0.8845 | 16 |
| DeepSeek | PCA-50 | Euclidean | 0.8701 | 16 |
| DeepSeek | linear | Euclidean | 0.8673 | 16 |
| DeepSeek | tangent subspace | geometry-aware | 0.8166 | 16 |

The signal is concentrated around layer 16 in these runs. The best probe is MLP for both judges, with linear close behind. This means the caving state is not subtle in this dataset: it is strongly recoverable from mid-layer residual activations.

The geometry-aware probes do not win per-turn. Tangent-subspace features are meaningfully above chance, but they trail the Euclidean baselines. Mahalanobis and graph-geodesic probes are weaker, around 0.72-0.73 AUROC.

### Trajectory Detection

The trajectory task asks whether a conversation is a sycophantic flip or stays steadfast-correct. This is closer to the original motivation, because the failure unfolds over several turns.

| judge | feature | probe | family | AUROC | layer |
| --- | --- | --- | --- | ---: | ---: |
| Opus | delta | linear | Euclidean | 0.9098 | 16 |
| Opus | delta | torch MLP | Euclidean | 0.9045 | 12 |
| Opus | final | tangent subspace | geometry-aware | 0.9025 | 19 |
| Opus | mean | tangent subspace | geometry-aware | 0.8995 | 16 |
| Opus | mean | linear | Euclidean | 0.8983 | 19 |
| DeepSeek | mean | linear | Euclidean | 0.9236 | 16 |
| DeepSeek | mean | tangent subspace | geometry-aware | 0.9174 | 16 |
| DeepSeek | mean | torch MLP | Euclidean | 0.9109 | 16 |
| DeepSeek | delta | torch MLP | Euclidean | 0.9104 | 12 |
| DeepSeek | delta | linear | Euclidean | 0.9082 | 12 |

This is the strongest result. Full-conversation trajectory summaries separate flips from steadfast-correct conversations at roughly 0.91-0.92 AUROC. The result holds under both Opus and DeepSeek labels.

The best trajectory features are simple summaries: mean state and start-to-end delta. That is useful, but it also limits the geometry claim. The model's pressured failure appears to leave a strong activation signature, but the current evidence does not show that this signature requires non-Euclidean geometry to detect.

## Confidence Intervals

The AUROCs above are single cross-validated point estimates. To attach uncertainty I ran a clustered percentile bootstrap (`experiments/bootstrap_ci.py`): for each headline number I reproduce the exact cross-validated out-of-fold predictions, then resample paired scenarios — not individual turns or conversations — with replacement 2,000 times and recompute AUROC. Resampling at the pair level matches the grouping used in cross-validation, so the interval is not deflated by treating the two arms of a scenario as independent. The point estimate equals the reported number; the interval reflects how far it moves as the scenario set is resampled.

| level | judge | best probe | AUROC | 95% CI |
| --- | --- | --- | ---: | :---: |
| per-turn | Opus | MLP @ L16 | 0.8791 | [0.856, 0.901] |
| per-turn | DeepSeek | MLP @ L16 | 0.8845 | [0.860, 0.907] |
| trajectory | Opus | delta + linear @ L16 | 0.9098 | [0.860, 0.952] |
| trajectory | DeepSeek | mean + linear @ L16 | 0.9236 | [0.881, 0.961] |
| trajectory | Opus | final + tangent subspace @ L19 | 0.9025 | [0.852, 0.945] |
| trajectory | DeepSeek | mean + tangent subspace @ L16 | 0.9174 | [0.874, 0.955] |

Two things follow. First, the per-turn signal is both strong and tightly estimated — the interval is narrow because it pools over 1,824 turns. Second, the trajectory intervals are wide, because the flip-vs-steadfast-correct contrast keeps only 167 (Opus) / 169 (DeepSeek) conversations — about 100 paired scenarios — and they overlap the per-turn intervals. So while the trajectory point estimates are consistently higher, the gain is not statistically separated at this sample size. The same caution applies to geometry: the tangent-subspace intervals sit almost entirely inside the linear-baseline intervals, so the geometry-vs-Euclidean comparison is inside the noise. The bootstrap resamples only the evaluation scenarios and holds the trained probes fixed, so it does not include probe-retraining or fold-assignment variance — the true uncertainty is, if anything, wider. Tightening these intervals — more scenarios, or a model that already knows more of the myths — is a first-order goal for the next iteration. Full numbers are in `results/eval/synthetic_pressure_llama8b/bootstrap_ci.json`.

## Interpretation

The experiment supports three claims.

First, pressure-induced caving is visible in activations. A probe trained on residual-stream activations can detect when the assistant accepts a false premise with high AUROC. This holds across two independent LLM judges.

Second, trajectories help — at least in point estimate. Conversation-level summaries give higher AUROCs than per-turn probes, which matches the intuition that caving under pressure is a process: a model can begin by resisting, then gradually soften or flip, and looking at the path gives more information than looking at isolated turns. At this pilot size the bootstrap intervals are wide enough that the trajectory advantage is suggestive rather than conclusive, but the direction is consistent across both judges and several feature/probe choices.

Third, the geometry hypothesis is not yet proven. Tangent-subspace probes are competitive in trajectory settings, but the best results still come from linear or MLP probes over simple Euclidean summaries. This means the result should be framed as strong evidence for activation monitoring and trajectory monitoring, not as evidence that non-Euclidean geometry has won.

The clean takeaway:

> In this synthetic pressure setting, Llama-3.1-8B-Instruct's internal activations reveal whether it is preserving truth or caving to a false user premise. Trajectory features make this signal stronger. Current geometry-aware probes are promising but do not yet beat Euclidean baselines.

## What I Achieved

Achieved:

- Generated a paired multi-turn pressure dataset.
- Rolled out Llama-3.1-8B-Instruct and extracted activations.
- Labeled the data with two independent judges.
- Fixed the evaluation to use paired-scenario grouping.
- Found a robust per-turn caving signal around 0.87-0.88 AUROC.
- Found a higher trajectory flip vs. steadfast-correct point estimate around 0.91-0.92 AUROC.
- Added clustered bootstrap confidence intervals, which show the per-turn signal is tight and the trajectory/geometry gaps are inside the noise at this sample size.
- Preserved the negative result: geometry-specific probes do not clearly outperform Euclidean baselines yet.

Not achieved yet:

- No publishable claim that non-Euclidean geometry is necessary.
- No statistically separated trajectory-over-per-turn gain (the intervals overlap).
- No cross-model result yet.
- No OOD transfer result yet.
- No causal intervention result yet.
- No human label audit yet.

## Limitations

The retained dataset is small. The generator produced 1,000 paired scenarios, but the knowledge filter retained only 114 — the model cleared the cold knowledge check on just those, since many of the myths are ones an 8B model itself believes. The bootstrap confidence intervals on the trajectory numbers are correspondingly wide, which confirms that this is a clean pilot result rather than a final claim: tightening it needs more retained scenarios and replication.

The labels are judge-model labels, not human labels. Using both Opus and DeepSeek helps because the main result survives both, but a human audit is still needed for the final draft.

The task is synthetic. That is a feature for control, because the false premise and correction are known, but it limits external validity. The next step should test transfer to natural sycophancy datasets or deception-proxy datasets.

The current probes are diagnostic, not causal. They show that the signal is present in activations. They do not prove that the probed direction or geometric object causes the model to cave.

## Next Experiments

The next draft should add:

1. More retained scenarios, to tighten the wide trajectory confidence intervals (a larger generator run, or a model that already knows more of the myths).
2. A small human audit of judge labels, especially hedge/accept and hedge/reject disagreements.
3. Early-warning evaluation: train on turns up to `k` and test whether the model will later flip.
4. OOD split: train on some pressure styles or domains and test on held-out styles/domains.
5. Cross-model check on a second open-weight model.
6. A stronger paired-deviation trajectory feature using pressured minus neutral paths.

The most important immediate next experiment is early warning. The current result shows I can detect caving and classify trajectories. The stronger safety result would be showing that activations predict a later flip before the assistant visibly caves.

The geometry-aware probe program — and where it could finally earn its keep over flat Euclidean summaries — is laid out with concrete win conditions in [`NEXT_STEPS.md`](NEXT_STEPS.md).
