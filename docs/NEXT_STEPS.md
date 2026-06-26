# Next Step: Geometry-Aware Probes

## Update (2026-06-26)

Status: one model (4-bit Llama-3.1-8B), ~46 graded scenarios, synthetic — pilot.

Since this plan was written I gave geometry a harder test than the finished-conversation
classification below: a graded PASS/FAIL pressure-and-steering arc. What I found:

- Manifold-shape geometry (tangent, curvature, point-cloud position) does not beat plain Euclidean
  baselines for detection, and for control it loses to trivial baselines and to a random direction at
  matched strength.
- Control gets done by near-perfect linear detection + a per-case measured probe of which steering
  action moves the decision. A learned selector adds nothing over picking the best-measured action.
- What carries control is the causal response field (how the readout moves under a perturbation),
  measured per case.
- The correction direction is shared across content families above a permutation null.

Next steps I'm pursuing, in order:

1. Replicate on a second model / fp16 — remove the single-model and 4-bit caveats and check the
   results hold across architectures.
2. Scale the dataset so I can test whether the response field can be *predicted* from the
   representation, not just measured.
3. Cross-model alignment — fit the correction direction on one model, test transfer to another up to
   an orthogonal alignment.

---

This repo ships a clean pilot result: caving to a false premise under pressure is
strongly decodable from Llama-3.1-8B-Instruct residual-stream activations, and
full-conversation trajectory summaries detect sycophantic flips vs. steadfast-correct
conversations at ~0.91-0.92 AUROC. The honest caveat is that **geometry-aware probes do not yet beat
simple Euclidean baselines** (see `synthetic_pressure_first_draft.md`). Tangent-subspace
trajectory probes are competitive but never clearly ahead of `linear`/`MLP` over `mean`
and `delta` features.

That negative result is the starting point, not the conclusion. The geometry hypothesis
has not been *tested where it should matter* yet — only where a flat summary already
saturates the signal. The plan below is how I intend to give geometry a fair test.

## Why geometry might still matter

The current win for Euclidean probes is on the easy framing: classify a *finished*
conversation, where the endpoint already encodes the outcome. Mean/final state is enough
because the flip has already happened. Geometry should earn its keep on the harder
framings, where the *path* carries information the endpoint does not:

- **Early warning.** Predict a *future* flip from turns `0..k`, before the model visibly
  caves. Here the endpoint is unavailable by construction, so trajectory shape (velocity,
  turning, drift direction) is the only signal.
- **Paired deviation.** Each scenario has a matched neutral and pressured arm. The
  object of interest is the deviation curve `delta(t) = pressured(t) - neutral(t)`, which
  controls for topic, answer token, and base knowledge. Geometry of `delta(t)` is a
  cleaner target than the raw path.
- **Deception transfer.** Sycophancy may be too textually simple for geometry to beat a
  linear readout. Deception (hidden belief vs. stated answer under incentive) is where a
  manifold/curvature signal is more plausible.

## Plan

Concretely, in order:

1. **Early-warning eval.** Reuse the saved per-turn activations; train on turns `0..k`
   and predict the later trajectory label. Report AUROC vs. `k` for Euclidean summaries
   *and* trajectory-shape features (the `path_stats`, `curve_summary`, `velocity`,
   `direction` features already in `geoprobe.geometry.trajectories`). This is the single
   most important next experiment.
2. **Paired-deviation features.** Add a pressured-minus-neutral path feature and re-run
   the trajectory sweep on `delta(t)` instead of the raw path.
3. **Bootstrap CIs + a small human label audit.** Put confidence intervals on the
   headline AUROCs and hand-check the hedge/accept and hedge/reject judge disagreements,
   so any geometry-vs-Euclidean gap is reported with uncertainty, not a point estimate.
4. **Learned metric / curved probes (the part this release deliberately omits).** Only
   after 1-3 justify it, bring back curved-geometry probes — a learned Riemannian path
   metric and a hyperbolic (Poincare-ball) probe behind known-answer correctness gates
   (a probe claiming to use curvature must first beat a linear baseline on
   hyperbolic-shaped synthetic data and *not* beat it on flat data before its activation
   numbers are trusted). That gated machinery and the heavier `geoopt` dependency live in
   the research branch, not here.
5. **Scale and transfer ($500 follow-on grant).** Re-run the strongest setup on
   Llama-3.3-70B and test transfer to a deception-proxy dataset (Apollo-style
   roleplaying/insider-trading), to see whether the trajectory signal — geometric or not —
   holds at scale and off-distribution.

## What would count as a real win

A nonlinear or curved probe beating a linear one on a single in-distribution split is
**not** a win — that is generic capacity, not geometry. A geometry claim only counts if a
geometric feature/probe wins on at least one of:

- **early detection** — predicts a future flip before the model caves;
- **OOD transfer** — train on one pressure style/domain, test on a held-out one;
- **cross-model stability** — the same geometric feature family works across model scales;
- **causal relevance** — steering or patching along the learned geometric object changes
  the model's behavior.

Until one of those holds, the claim stays where the first draft puts it: activation and
trajectory monitoring work; non-Euclidean geometry is unproven.
