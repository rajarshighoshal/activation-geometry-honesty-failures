# Synthetic Pressure Final Summary

All numbers below are read from saved JSON files.

## Label Agreement

Opus vs DeepSeek turn agreement: 1542/1824 = 84.54%.
Exact conversation agreement: 74/228.

## Trajectory Taxonomy

| judge | self_correction | sycophantic_flip | steadfast_wrong | steadfast_correct | accept_turns |
| --- | --- | --- | --- | --- | --- |
| opus | 55 | 79 | 6 | 88 | 433 |
| deepseek | 51 | 77 | 8 | 92 | 421 |

## Per-Turn Probes

| judge | probe | family | AUROC | layer |
| --- | --- | --- | --- | --- |
| opus | mlp | euclidean | 0.8791 | 16 |
| opus | linear | euclidean | 0.8713 | 16 |
| opus | pca50 | euclidean | 0.8585 | 16 |
| opus | tangent_subspace | manifold | 0.8073 | 16 |
| opus | graph_geodesic | manifold | 0.7244 | 16 |
| opus | mahalanobis | metric | 0.7193 | 16 |
| opus | class_mahalanobis | metric | 0.7188 | 16 |
| opus | centroid | euclidean | 0.7171 | 16 |
| deepseek | mlp | euclidean | 0.8845 | 16 |
| deepseek | pca50 | euclidean | 0.8701 | 16 |
| deepseek | linear | euclidean | 0.8673 | 16 |
| deepseek | tangent_subspace | manifold | 0.8166 | 16 |
| deepseek | graph_geodesic | manifold | 0.732 | 16 |
| deepseek | mahalanobis | metric | 0.7273 | 16 |
| deepseek | class_mahalanobis | metric | 0.727 | 16 |
| deepseek | centroid | euclidean | 0.7259 | 16 |

## Trajectory Probes

| judge | feature | probe | family | AUROC | layer |
| --- | --- | --- | --- | --- | --- |
| opus | delta | linear | euclidean | 0.9098 | 16 |
| opus | delta | torch_mlp | euclidean | 0.9045 | 12 |
| opus | final | tangent_subspace | manifold | 0.9025 | 19 |
| opus | mean | tangent_subspace | manifold | 0.8995 | 16 |
| opus | mean | linear | euclidean | 0.8983 | 19 |
| opus | final | torch_mlp | euclidean | 0.8859 | 16 |
| opus | mean | torch_mlp | euclidean | 0.8852 | 8 |
| opus | delta | tangent_subspace | manifold | 0.8839 | 16 |
| deepseek | mean | linear | euclidean | 0.9236 | 16 |
| deepseek | mean | tangent_subspace | manifold | 0.9174 | 16 |
| deepseek | mean | torch_mlp | euclidean | 0.9109 | 16 |
| deepseek | delta | torch_mlp | euclidean | 0.9104 | 12 |
| deepseek | delta | linear | euclidean | 0.9082 | 12 |
| deepseek | final | torch_mlp | euclidean | 0.9034 | 12 |
| deepseek | final | linear | euclidean | 0.9018 | 12 |
| deepseek | path_flat | linear | euclidean | 0.9012 | 16 |

## Confidence Intervals

Clustered percentile bootstrap over paired scenarios on cross-validated out-of-fold predictions.

| level | judge | probe | AUROC | 95% CI |
| --- | --- | --- | --- | --- |
| per_turn | Opus 4.8 | per-turn mlp | 0.8791 | [0.8564, 0.9006] |
| per_turn | DeepSeek v4 Pro | per-turn mlp | 0.8845 | [0.8600, 0.9074] |
| trajectory | Opus 4.8 | delta + linear | 0.9098 | [0.8603, 0.9518] |
| trajectory | DeepSeek v4 Pro | mean + linear | 0.9236 | [0.8805, 0.9614] |
| trajectory | Opus 4.8 | final + tangent_subspace | 0.9025 | [0.8522, 0.9445] |
| trajectory | DeepSeek v4 Pro | mean + tangent_subspace | 0.9174 | [0.8738, 0.9553] |

## Interpretation Guardrail

If linear/MLP remain strongest, report that the signal is strongly recoverable but current geometry-aware probes do not outperform basic Euclidean baselines.
