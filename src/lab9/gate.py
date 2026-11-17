"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.eval import SPEC, load_spec, per_item
from lab9.graders import GRADERS


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """M7 (Expert): refuse to compare reports that cannot be trusted. Return a list of problems
    (empty = trustworthy). A gate that passes a broken report is worse than no gate.
    Must catch at least:
      - any metric value in pr["metrics"] that is NaN or inf
      - len(pr["rows"]) != manifest items x len(manifest seeds)   (dropped / duplicated rows)
      - the (item_id, seed) set of PR differs from the baseline's (cherry-picked seeds/items)
      - pr["evaluator_failures"] non-empty, or a row whose value for a graded spec metric is
        None (a crashed grader silently scores as "missing" and drops out of the mean)
      - base_spec given and a threshold in spec is LOOSER than in base_spec for the same
        eval-set version (ratchet: max may not rise, min may not fall, a blocking metric may
        not become non-blocking, a metric may not disappear; the same for spec["slices"],
        including dropping no_significant_drop)
      - an item's slice tags in PR rows differ from the baseline's (relabelling an item out of a
        slice hides its regression from the slice gate)"""
    problems: list[str] = []
    for metric, value in pr.get("metrics", {}).items():
        if isinstance(value, float) and not math.isfinite(value):
            problems.append(f"metric {metric} is not finite")

    manifest = pr.get("manifest") or {}
    rows = pr.get("rows") or []
    expected_rows = int(manifest.get("items") or 0) * len(manifest.get("seeds") or [])
    if len(rows) != expected_rows:
        problems.append(f"row count {len(rows)} != manifest {expected_rows}")

    keys = [(row.get("item_id"), row.get("seed")) for row in rows]
    if len(set(keys)) != len(keys):
        problems.append("duplicate (item_id, seed) row")
    base_keys = {(row.get("item_id"), row.get("seed")) for row in base.get("rows") or []}
    if set(keys) != base_keys:
        problems.append("(item_id, seed) set differs from baseline")

    if pr.get("evaluator_failures"):
        problems.append("evaluator_failures is non-empty")
    graded = {metric["id"] for metric in spec.get("metrics") or [] if metric["id"] in GRADERS}
    for row in rows:
        for metric in graded:
            if row.get(metric) is None:
                problems.append(f"{row.get('item_id')}@{row.get('seed')}: {metric} is missing")
                break

    base_slices = {(row.get("item_id"), row.get("seed")): tuple(row.get("slices") or [])
                   for row in base.get("rows") or []}
    for row in rows:
        key = (row.get("item_id"), row.get("seed"))
        if key in base_slices and tuple(row.get("slices") or []) != base_slices[key]:
            problems.append(f"{key[0]}@{key[1]}: slice tags differ from baseline")

    if base_spec and spec.get("eval_set_version") == base_spec.get("eval_set_version"):
        current_metrics = {metric["id"]: metric for metric in spec.get("metrics") or []}
        for old in base_spec.get("metrics") or []:
            metric_id = old["id"]
            new = current_metrics.get(metric_id)
            if new is None:
                problems.append(f"ratchet: metric {metric_id} was removed")
                continue
            if old.get("blocking") and not new.get("blocking"):
                problems.append(f"ratchet: metric {metric_id} is no longer blocking")
            problems.extend(_threshold_loosened(old.get("threshold") or {}, new.get("threshold") or {},
                                                f"metric {metric_id}"))

        current_slices = {rule["name"]: rule for rule in spec.get("slices") or []}
        for old in base_spec.get("slices") or []:
            name = old["name"]
            new = current_slices.get(name)
            if new is None:
                problems.append(f"ratchet: slice {name} was removed")
                continue
            if old.get("metric") != new.get("metric"):
                problems.append(f"ratchet: slice {name} metric changed")
            if old.get("blocking") and not new.get("blocking"):
                problems.append(f"ratchet: slice {name} is no longer blocking")
            problems.extend(_threshold_loosened(old, new, f"slice {name}"))
    return problems


def _threshold_loosened(old: dict, new: dict, label: str) -> list[str]:
    problems: list[str] = []
    if "min" in old and ("min" not in new or new["min"] < old["min"]):
        problems.append(f"ratchet: {label} min was lowered")
    if "max" in old and ("max" not in new or new["max"] > old["max"]):
        problems.append(f"ratchet: {label} max was raised")
    if old.get("no_significant_drop") and not new.get("no_significant_drop"):
        problems.append(f"ratchet: {label} removed no_significant_drop")
    return problems


def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    blocked: list[str] = []
    lines: list[str] = []
    bootstrap = spec.get("bootstrap", {})
    for rule in spec.get("slices") or []:
        name, metric = rule["name"], rule["metric"]
        identifier = f"slice:{name}/{metric}"
        current = per_item(pr, metric, slice_name=name)
        baseline = per_item(base, metric, slice_name=name)
        values = list(current.values())
        value = sum(values) / len(values) if values else None
        verdict, note = "ok", ""
        if value is None:
            verdict = "missing"
        elif "min" in rule and value < rule["min"]:
            verdict = "fail"

        if rule.get("no_significant_drop") and value is not None:
            keys = sorted(set(current) & set(baseline))
            if keys:
                delta, low, high = stats.paired_bootstrap(
                    [current[key] for key in keys],
                    [baseline[key] for key in keys],
                    n_resamples=bootstrap.get("n_resamples", 1000),
                    rng=bootstrap.get("rng", 2027),
                    confidence=bootstrap.get("confidence", 0.95),
                )
                note = f"Δ {delta:+.3f} CI [{low:+.3f}, {high:+.3f}]"
                if high < 0:
                    verdict = "fail"

        if verdict != "ok" and rule.get("blocking"):
            blocked.append(identifier)
        label = {"ok": "ok", "missing": "MISSING"}.get(
            verdict, "BLOCK" if rule.get("blocking") else "warn"
        )
        threshold = {k: rule[k] for k in ("min", "no_significant_drop") if k in rule}
        lines.append(f"  {identifier:<35} {value!s:<8} {json.dumps(threshold):<40} {note:<28} {label}")
    return blocked, lines


def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    if pr["manifest"]["eval_set_sha"] != base["manifest"]["eval_set_sha"]:
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid):
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            keys = sorted(set(a) & set(b))
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                                               n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            if hi < 0:
                verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    print(f"gate: PR {pr['run_id']} vs main {base['run_id']} · eval set {pr['manifest']['eval_set_sha']}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
