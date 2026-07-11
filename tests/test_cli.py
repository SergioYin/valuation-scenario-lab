from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "valuation_scenario_lab.cli", *args],
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_build_packet_compare_ledger_and_matrix(tmp_path: Path) -> None:
    out = tmp_path / "demo"
    assert run_cli("build-packet", "--fixtures", str(ROOT / "examples"), "--output", str(out)).returncode == 0
    packet = json.loads((out / "valuation-packet.json").read_text(encoding="utf-8"))
    assert packet["schema_version"] == "valuation-scenario-lab.v0.3"
    assert "No buy/sell/hold advice." in packet["boundaries"]

    assert run_cli("compare-history", "--current", str(out / "valuation-packet.json"), "--prior", str(ROOT / "examples" / "prior-packet.json"), "--output", str(out)).returncode == 0
    assert run_cli("review-ledger", "--packet", str(out / "valuation-packet.json"), "--policy", str(ROOT / "examples" / "review-policy.json"), "--output", str(out)).returncode == 0
    assert run_cli("sensitivity-matrix", "--fixtures", str(ROOT / "examples"), "--output", str(out)).returncode == 0
    matrix = json.loads((out / "sensitivity-matrix.json").read_text(encoding="utf-8"))
    assert len(matrix["rows"]) == 9

    assert run_cli("decision-journal", "--packet", str(out / "valuation-packet.json"), "--ledger", str(out / "review-ledger.json"), "--output", str(out)).returncode == 0
    journal = json.loads((out / "decision-journal.json").read_text(encoding="utf-8"))
    assert journal["summary_decision"] == "research packet logged; no action recommendation"
    assert "No buy/sell/hold advice." in journal["boundaries"]

    landing = run_cli("public-readiness-landing", "--root", str(ROOT), "--output", str(out))
    assert landing.returncode == 0, landing.stdout + landing.stderr
    landing_payload = json.loads((out / "public-readiness-landing.json").read_text(encoding="utf-8"))
    assert landing_payload["schema_version"] == "valuation-scenario-lab.public-readiness.v0.3"
    assert "zero runtime dependencies" in landing_payload["readiness_checks"]


def test_release_validation_and_maturity() -> None:
    validation = run_cli("validate-release", "--root", str(ROOT))
    assert validation.returncode == 0, validation.stdout + validation.stderr
    payload = json.loads(validation.stdout)
    assert payload["status"] == "pass"

    maturity = run_cli("maturity-report", "--root", str(ROOT))
    assert maturity.returncode == 0
    assert json.loads(maturity.stdout)["score"] >= 90


def test_selfcheck_accepts_root_from_empty_cwd(tmp_path: Path) -> None:
    result = run_cli("selfcheck", "--root", str(ROOT), cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "selfcheck passed" in result.stdout


def test_quickstart_check_and_visual_receipt(tmp_path: Path) -> None:
    out = tmp_path / "demo"
    quickstart = run_cli("quickstart-check", "--root", str(ROOT), "--output", str(out))
    assert quickstart.returncode == 0, quickstart.stdout + quickstart.stderr
    quickstart_payload = json.loads((out / "quickstart-check.json").read_text(encoding="utf-8"))
    assert quickstart_payload["status"] == "pass"
    assert quickstart_payload["fixture_source"] == "local-or-packaged-fixtures"
    assert (out / "quickstart-check.md").exists()
    assert (out / "decision-journal.md").exists()
    assert (out / "public-readiness-landing.html").exists()

    receipt = run_cli("visual-receipt", "--root", str(ROOT), "--output", str(out))
    assert receipt.returncode == 0, receipt.stdout + receipt.stderr
    receipt_payload = json.loads((out / "visual-receipt.json").read_text(encoding="utf-8"))
    assert receipt_payload["schema_version"] == "valuation-scenario-lab.visual-receipt.v0.3"
    assert receipt_payload["artifact_count"] == 14
    assert "No buy/sell/hold advice." in (out / "visual-receipt.html").read_text(encoding="utf-8")
