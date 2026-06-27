# Follow-Up Directions

This page lists high-level follow-up directions for the public artifact.

## Completed Status

The completed pilot results establish four points:

- pressure-induced caving is visible in Llama-3.1-8B activations;
- trajectory summaries have higher point estimates than per-turn probes, but the pilot is
  not yet large enough to separate that gain cleanly;
- tangent-subspace and local point-cloud features are competitive diagnostics, while
  Euclidean linear/MLP baselines remain the strongest simple reference point in this
  artifact;
- directional steering audits are necessary, because aggregate correction rates can hide
  one-way label pushing.

## Follow-Up Directions

1. **Replication.** Re-run the strongest completed evaluations on additional random
   splits and, where feasible, a second open-weight model.
2. **Scale.** Increase the retained scenario count so trajectory and geometry-vs-linear
   comparisons have tighter confidence intervals.
3. **Transfer.** Test whether the monitoring and steering results survive changes in
   pressure style, content family, and model family.
4. **Control baselines.** Compare intervention methods against linear, route-wise,
   random, measured-action, and abstention-aware baselines on the same held-out rows.
5. **Human audit.** Add a small human check of judge labels and strict-basis steering
   audits before making stronger claims about reasoning quality.
6. **Richer geometry.** Evaluate stronger geometry-aware methods only under the same
   audit standard: grouped splits, directional fix/harm tables, coherence checks, strict
   basis checks, and matched baselines.

## Reporting Standard

Future updates should report:

- grouped train/test splits;
- confidence intervals over scenarios, not individual turns alone;
- fixes and harms split by error direction;
- parse/coherence and strict-basis quality;
- simple baselines run on the same examples.

That standard is the main lesson of the control audit: a method can look strong in an
aggregate table while failing one direction or relying on abstention for safety.
