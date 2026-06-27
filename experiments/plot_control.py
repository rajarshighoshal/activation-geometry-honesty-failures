"""Generate the graded-control figures from directional_audit_summary.json.

Same paper style as plot_summary.py (experiments/paper_style.py). Reads only the committed
sanitized summary, writes figures/graded_control/*.{svg,png,pdf}.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import paper_style as ps


def ramp_figure(summary: dict, out: Path) -> None:
    ramp = summary["ramp"]["p_deceptive_by_level"]
    levels = sorted(int(k) for k in ramp)
    ys = [ramp[str(level)] for level in levels]
    fig, ax = plt.subplots(figsize=(4.7, 2.6))
    ax.plot(levels, ys, "-o", color=ps.CB["blue"], ms=5, lw=1.8, zorder=3)
    ax.set_xlabel("pressure level (p0 - p6)")
    ax.set_ylabel("P(false report)")
    ax.set_ylim(0, 1)
    ax.set_xticks(levels)
    ax.set_title("False-report rate rises monotonically with pressure", loc="left")
    ps.save(fig, out)


def cosines_figure(summary: dict, out: Path) -> None:
    dc = summary["direction_cosines"]
    layers = sorted(dc, key=lambda L: int(L[1:]))
    series = [
        ("cos_to_PASS_to_FAIL", "cos(to_PASS, to_FAIL)", ps.CB["purple"]),
        ("cos_pooled_to_PASS", "cos(pooled, to_PASS)", ps.CB["blue"]),
        ("cos_pooled_to_FAIL", "cos(pooled, to_FAIL)", ps.CB["red"]),
    ]
    x = np.arange(len(layers))
    fig, ax = plt.subplots(figsize=(5.0, 2.7))
    for key, label, color in series:
        ax.plot(x, [dc[L][key] for L in layers], "-o", color=color, ms=4, lw=1.6, label=label, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(layers)
    ax.set_xlabel("layer")
    ax.set_ylabel("cosine")
    ax.set_ylim(0.5, 1.0)
    ax.set_title("Correction directions are positively aligned, not opposite", loc="left")
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    ps.save(fig, out)


def directional_rates_figure(summary: dict, out: Path) -> None:
    rows = summary["oracle_control"]
    metrics = [
        ("false_FAIL_to_PASS_fix", "false_FAIL→PASS fix", ps.CB["green"]),
        ("false_PASS_to_FAIL_fix", "false_PASS→FAIL fix", ps.CB["red"]),
        ("honest_PASS_preserved", "honest_PASS kept", ps.CB["blue"]),
        ("honest_FAIL_preserved", "honest_FAIL kept", ps.CB["orange"]),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.9), sharey=True)
    for ax, method in zip(axes, ("bidir_linear", "bidir_tangent")):
        mrows = sorted((r for r in rows if r["method"] == method), key=lambda r: r["alpha"])
        xs = [r["alpha"] for r in mrows]
        for key, label, color in metrics:
            ax.plot(xs, [r[key] for r in mrows], "-o", color=color, ms=4, lw=1.5, label=label, zorder=3)
        ax.set_title(method.replace("bidir_", ""), loc="left")
        ax.set_xlabel("steering alpha")
        ax.set_xticks(xs)
        ax.set_ylim(-0.05, 1.05)
    axes[0].set_ylabel("rate")
    axes[1].legend(frameon=False, fontsize=6.5, loc="center left", bbox_to_anchor=(1.0, 0.5))
    ps.save(fig, out)


def powered_followup_figure(summary: dict, out: Path) -> None:
    rows = summary["policies"]
    label_map = {
        "fixed tangent": "fixed\ntangent",
        "route hybrid": "route\nhybrid",
        "context geom best": "context\ngeom",
        "response geom best": "response\ngeom",
        "target-margin argmax": "margin\nargmax",
    }
    labels = [label_map.get(row["label"], row["label"]) for row in rows]
    status = [row["deceptive_status_fixes"] for row in rows]
    strict = [row["deceptive_strict_fixes"] for row in rows]
    harms = [row["honest_status_harms"] for row in rows]
    xs = np.arange(len(rows))
    width = 0.36
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    ax.bar(xs - width / 2, status, width=width, color=ps.CB["blue"],
           label="status fixes", zorder=3)
    ax.bar(xs + width / 2, strict, width=width, color=ps.CB["green"],
           label="strict fixes", zorder=3)
    for x, harm in zip(xs, harms):
        ax.plot([x], [harm], "x", color=ps.CB["red"], ms=5, mew=1.4, zorder=4)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.set_ylabel("count")
    ax.set_ylim(0, 82)
    ax.set_title("Decision-token control: measured response dominates", loc="left")
    ax.grid(axis="x", visible=False)
    handles, handle_labels = ax.get_legend_handles_labels()
    handles.append(plt.Line2D([], [], marker="x", linestyle="", color=ps.CB["red"],
                              label="honest harms"))
    ax.legend(handles=handles, frameon=False, loc="upper left", ncol=3, fontsize=7)
    ps.save(fig, out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", default="results/eval/graded_control/directional_audit_summary.json")
    parser.add_argument("--powered-summary", default="results/eval/graded_control/powered_followup_summary.json")
    parser.add_argument("--out-dir", default="figures/graded_control")
    args = parser.parse_args()

    ps.apply()
    summary = json.loads(Path(args.summary).read_text())
    out_dir = Path(args.out_dir)
    ramp_figure(summary, out_dir / "graded_pressure_ramp.png")
    cosines_figure(summary, out_dir / "bidirectional_direction_cosines.png")
    directional_rates_figure(summary, out_dir / "bidirectional_control_directional_rates.png")
    powered_path = Path(args.powered_summary)
    if powered_path.exists():
        powered = json.loads(powered_path.read_text())
        powered_followup_figure(powered, out_dir / "powered_followup_policy_comparison.png")
    for name in ("graded_pressure_ramp", "bidirectional_direction_cosines",
                 "bidirectional_control_directional_rates", "powered_followup_policy_comparison"):
        print(f"wrote {out_dir / name}.{{svg,png,pdf}}")


if __name__ == "__main__":
    main()
