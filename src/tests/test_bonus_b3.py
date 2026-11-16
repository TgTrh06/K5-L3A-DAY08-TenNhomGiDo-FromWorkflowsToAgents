import json
from pathlib import Path
import pytest

from bonus.swarm_verified import run_claim
from lab8.db import connect, init_store
from lab8.metrics import trial_pass
from tests.conftest import BY_ID, CLAIMS, WORLD


def test_swarm_verified_fixes_seed_55_variance(tmp_path):
    """Seed 55 fails on standard swarm due to trusting ticket over order row.

    SwarmVerified intercepts the discrepancy via the deterministic verifier gate
    and passes successfully.
    """
    store = tmp_path / "t02-verified-55.sqlite"
    init_store(store, WORLD, CLAIMS).close()

    result = run_claim("C-002", seed=55, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-002"]["expected"], conn)
    finally:
        conn.close()

    assert passed, reason
    assert result.status == "denied"

    # Confirm that verifier_override was emitted in trace
    trace_data = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    events = [ev["kind"] for ev in trace_data["events"]]
    assert "verifier_override" in events


def test_swarm_verified_on_adversarial_cases(tmp_path):
    """Verify SwarmVerified handles all 8 adversarial cases correctly."""
    bonus_dir = Path(__file__).resolve().parent.parent / "bonus"
    adv_world = json.loads((bonus_dir / "world.json").read_text(encoding="utf-8"))
    
    adv_claims = []
    with open(bonus_dir / "cases.jsonl", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                adv_claims.append(json.loads(line))
    adv_by_id = {c["claim_id"]: c for c in adv_claims}

    for claim in adv_claims:
        cid = claim["claim_id"]
        store = tmp_path / f"adv-{cid}.sqlite"
        init_store(store, adv_world, adv_claims).close()
        result = run_claim(cid, seed=55, store_path=str(store))
        conn = connect(store)
        try:
            passed, reason = trial_pass(result.as_dict(), adv_by_id[cid]["expected"], conn)
        finally:
            conn.close()
        assert passed, f"Claim {cid} failed: {reason}"
