from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden"


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


def golden_snapshot(name: str) -> dict:
    return json.loads((GOLDEN / name).read_text(encoding="utf-8"))


def key_demo_snapshot(out: Path) -> dict:
    packet = json.loads((out / "valuation-packet.json").read_text(encoding="utf-8"))
    gallery = json.loads((out / "multi-company-demo-gallery.json").read_text(encoding="utf-8"))
    doctor = json.loads((out / "fixture-doctor.json").read_text(encoding="utf-8"))
    return {
        "valuation_packet": {
            "schema_version": packet["schema_version"],
            "company": packet["company"],
            "ticker": packet["ticker"],
            "weighted_fair_value_per_share": packet["weighted_fair_value_per_share"],
            "weighted_range_per_share": packet["weighted_range_per_share"],
            "weighted_margin_of_safety_pct": packet["weighted_margin_of_safety_pct"],
            "margin_of_safety_label": packet["margin_of_safety_label"],
            "scenario_bases": [item["base"] for item in packet["valuation_ranges"]],
            "boundaries": packet["boundaries"],
        },
        "demo_gallery": {
            "schema_version": gallery["schema_version"],
            "company_count": gallery["company_count"],
            "tickers": [item["ticker"] for item in gallery["cards"]],
            "fair_values": [item["weighted_fair_value_per_share"] for item in gallery["cards"]],
        },
        "fixture_doctor": {
            "schema_version": doctor["schema_version"],
            "status": doctor["status"],
            "fixture_count": doctor["fixture_count"],
            "issue_count": doctor["issue_count"],
            "files": doctor["files"],
        },
    }


def test_build_packet_compare_ledger_and_matrix(tmp_path: Path) -> None:
    out = tmp_path / "demo"
    assert run_cli("build-packet", "--fixtures", str(ROOT / "examples"), "--output", str(out)).returncode == 0
    packet = json.loads((out / "valuation-packet.json").read_text(encoding="utf-8"))
    assert packet["schema_version"] == "valuation-scenario-lab.v0.5"
    assert "No buy/sell/hold advice." in packet["boundaries"]

    assert run_cli("compare-history", "--current", str(out / "valuation-packet.json"), "--prior", str(ROOT / "examples" / "prior-packet.json"), "--output", str(out)).returncode == 0
    assert run_cli("review-ledger", "--packet", str(out / "valuation-packet.json"), "--policy", str(ROOT / "examples" / "review-policy.json"), "--output", str(out)).returncode == 0
    assert run_cli("sensitivity-matrix", "--fixtures", str(ROOT / "examples"), "--output", str(out)).returncode == 0
    matrix = json.loads((out / "sensitivity-matrix.json").read_text(encoding="utf-8"))
    assert len(matrix["rows"]) == 9

    assert run_cli("assumption-change-walkthrough", "--fixtures", str(ROOT / "examples"), "--output", str(out)).returncode == 0
    walkthrough = json.loads((out / "assumption-change-walkthrough.json").read_text(encoding="utf-8"))
    assert walkthrough["schema_version"] == "valuation-scenario-lab.assumption-change.v0.5"
    assert walkthrough["changed_assumption"] == "fcf_margin_pct"
    assert "No buy/sell/hold advice." in walkthrough["boundaries"]
    assert (out / "assumption-change-walkthrough.html").exists()

    assert run_cli("demo-gallery", "--fixtures", str(ROOT / "examples"), "--output", str(out)).returncode == 0
    gallery = json.loads((out / "multi-company-demo-gallery.json").read_text(encoding="utf-8"))
    assert gallery["schema_version"] == "valuation-scenario-lab.demo-gallery.v0.5"
    assert gallery["company_count"] == 2
    assert {item["ticker"] for item in gallery["cards"]} == {"EXCO", "NIMB"}
    assert "No buy/sell/hold advice." in (out / "multi-company-demo-gallery.html").read_text(encoding="utf-8")

    assert run_cli("decision-journal", "--packet", str(out / "valuation-packet.json"), "--ledger", str(out / "review-ledger.json"), "--output", str(out)).returncode == 0
    journal = json.loads((out / "decision-journal.json").read_text(encoding="utf-8"))
    assert journal["summary_decision"] == "research packet logged; no action recommendation"
    assert "No buy/sell/hold advice." in journal["boundaries"]

    landing = run_cli("public-readiness-landing", "--root", str(ROOT), "--output", str(out))
    assert landing.returncode == 0, landing.stdout + landing.stderr
    landing_payload = json.loads((out / "public-readiness-landing.json").read_text(encoding="utf-8"))
    assert landing_payload["schema_version"] == "valuation-scenario-lab.public-readiness.v0.5"
    assert "zero runtime dependencies" in landing_payload["readiness_checks"]
    assert "demo/multi-company-demo-gallery.html" in landing_payload["demo_outputs"]

    showcase = run_cli("showcase-dashboard", "--root", str(ROOT), "--output", str(out))
    assert showcase.returncode == 0, showcase.stdout + showcase.stderr
    showcase_payload = json.loads((out / "showcase-dashboard.json").read_text(encoding="utf-8"))
    assert showcase_payload["schema_version"] == "valuation-scenario-lab.showcase-dashboard.v0.6"
    assert showcase_payload["fixture_doctor_status"] == "pass"
    assert showcase_payload["sensitivity_case_count"] == 9
    svg = (out / "showcase-dashboard.svg").read_text(encoding="utf-8")
    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert "<script" not in svg.lower()
    assert "Valuation Scenario Lab Showcase Dashboard" in svg
    assert "Fixture doctor" in svg
    assert "Sensitivity matrix" in svg
    assert "No buy/sell/hold advice." in svg

    thesis = run_cli("thesis-brief", "--root", str(ROOT), "--output", str(out))
    assert thesis.returncode == 0, thesis.stdout + thesis.stderr
    thesis_payload = json.loads((out / "thesis-brief.json").read_text(encoding="utf-8"))
    assert thesis_payload["schema_version"] == "valuation-scenario-lab.thesis-brief.v0.7"
    assert thesis_payload["journal_summary"] == "research packet logged; no action recommendation"
    assert thesis_payload["fixture_quality"]["status"] == "pass"
    assert "demo/showcase-dashboard.json" in thesis_payload["evidence_artifacts"]
    assert "No buy/sell/hold advice." in (out / "thesis-brief.html").read_text(encoding="utf-8")
    assert "<script" not in (out / "thesis-brief.html").read_text(encoding="utf-8").lower()

    library = run_cli("scenario-library", "--fixtures", str(ROOT / "examples"), "--output", str(out))
    assert library.returncode == 0, library.stdout + library.stderr
    library_payload = json.loads((out / "scenario-library.json").read_text(encoding="utf-8"))
    assert library_payload["schema_version"] == "valuation-scenario-lab.scenario-library.v0.7"
    assert library_payload["company_count"] == 2
    assert library_payload["card_count"] == 6
    assert library_payload["cards"][0]["id"] == "EXCO-base-reinvestment-case"
    assert "No broker connections." in library_payload["boundaries"]
    assert "<script" not in (out / "scenario-library.html").read_text(encoding="utf-8").lower()

    workflow = run_cli("sample-workflow", "--root", str(ROOT), "--output", str(out))
    assert workflow.returncode == 0, workflow.stdout + workflow.stderr
    workflow_payload = json.loads((out / "sample-workflow.json").read_text(encoding="utf-8"))
    assert workflow_payload["schema_version"] == "valuation-scenario-lab.sample-workflow.v0.8"
    assert workflow_payload["steps"][0]["command"] == "valuation-scenario-lab demo --root ."
    assert "demo/reproducibility-audit.html" in workflow_payload["steps"][-2]["artifacts"]
    assert "release/public-bundle.html" in workflow_payload["steps"][-1]["artifacts"]
    assert "No buy/sell/hold advice." in (out / "sample-workflow.html").read_text(encoding="utf-8")
    assert "<script" not in (out / "sample-workflow.html").read_text(encoding="utf-8").lower()

    audit = run_cli("reproducibility-audit", "--root", str(ROOT), "--output", str(out))
    assert audit.returncode == 0, audit.stdout + audit.stderr
    audit_payload = json.loads((out / "reproducibility-audit.json").read_text(encoding="utf-8"))
    assert audit_payload["schema_version"] == "valuation-scenario-lab.reproducibility-audit.v0.8"
    assert audit_payload["status"] == "pass"
    assert audit_payload["checks"]["artifact_presence"]["status"] == "pass"
    assert audit_payload["checks"]["schema_versions"]["status"] == "pass"
    assert audit_payload["checks"]["zero_dependency_metadata"]["status"] == "pass"
    assert audit_payload["checks"]["safety_boundary_coverage"]["status"] == "pass"
    assert "No live data." in (out / "reproducibility-audit.html").read_text(encoding="utf-8")
    assert "<script" not in (out / "reproducibility-audit.html").read_text(encoding="utf-8").lower()

    template = run_cli("new-fixture-template", "--output", str(out / "onboarding-template"))
    assert template.returncode == 0, template.stdout + template.stderr
    template_company = json.loads((out / "onboarding-template" / "company.json").read_text(encoding="utf-8"))
    template_policy = json.loads((out / "onboarding-template" / "review-policy.json").read_text(encoding="utf-8"))
    template_prior = json.loads((out / "onboarding-template" / "prior-packet.json").read_text(encoding="utf-8"))
    assert template_company["company"] == "Northstar Kitchens Collective"
    assert len(template_company["scenarios"]) == 3
    assert sum(item["weight"] for item in template_company["scenarios"]) == 1.0
    assert template_policy["freshness_limit_days"] == 45
    assert template_prior["schema_version"] == "valuation-scenario-lab.prior-packet-template.v0.9"
    assert "No broker connections." in (out / "onboarding-template" / "README.md").read_text(encoding="utf-8")

    casebook = run_cli("casebook", "--root", str(ROOT), "--output", str(out))
    assert casebook.returncode == 0, casebook.stdout + casebook.stderr
    casebook_payload = json.loads((out / "casebook.json").read_text(encoding="utf-8"))
    assert casebook_payload["schema_version"] == "valuation-scenario-lab.casebook.v0.9"
    assert [item["section"] for item in casebook_payload["walkthrough"]] == [
        "Packet",
        "Scenario Library",
        "Thesis Brief",
        "Workflow Receipt",
        "Reproducibility Audit",
    ]
    assert "demo/reproducibility-audit.json" in casebook_payload["source_artifacts"]
    assert "No buy/sell/hold advice." in (out / "casebook.html").read_text(encoding="utf-8")
    assert "<script" not in (out / "casebook.html").read_text(encoding="utf-8").lower()

    release_out = tmp_path / "release"
    smoke = run_cli("install-smoke-receipt", "--root", str(ROOT), "--output", str(release_out))
    assert smoke.returncode == 0, smoke.stdout + smoke.stderr
    smoke_payload = json.loads((release_out / "install-smoke-receipt.json").read_text(encoding="utf-8"))
    assert smoke_payload["schema_version"] == "valuation-scenario-lab.install-smoke-receipt.v1.0"
    assert smoke_payload["status"] == "documented"
    assert all(not item["network_required"] for item in smoke_payload["entry_point_smoke_commands"])
    assert "valuation-scenario-lab selfcheck" in [item["command"] for item in smoke_payload["entry_point_smoke_commands"]]
    assert "No live data." in (release_out / "install-smoke-receipt.html").read_text(encoding="utf-8")
    assert "<script" not in (release_out / "install-smoke-receipt.html").read_text(encoding="utf-8").lower()

    bundle = run_cli("export-bundle", "--root", str(ROOT), "--output", str(release_out))
    assert bundle.returncode == 0, bundle.stdout + bundle.stderr
    bundle_payload = json.loads((release_out / "public-bundle.json").read_text(encoding="utf-8"))
    assert bundle_payload["schema_version"] == "valuation-scenario-lab.public-bundle.v1.0"
    assert bundle_payload["status"] == "pass"
    bundle_files = {item["path"]: item for item in bundle_payload["files"]}
    assert bundle_files["demo/valuation-packet.html"]["category"] == "public-demo-artifact"
    assert bundle_files["release/install-smoke-receipt.json"]["category"] == "release-asset"
    assert bundle_files["skills/agent/valuation-scenario-lab/SKILL.md"]["category"] == "skill-file"
    assert bundle_files["README.md"]["packaged_data_file"] is True
    assert len(bundle_files["README.md"]["sha256"]) == 64
    assert "release/public-bundle.json" in [item["path"] for item in bundle_payload["self_outputs"]]
    assert "No buy/sell/hold advice." in (release_out / "public-bundle.html").read_text(encoding="utf-8")
    assert "<script" not in (release_out / "public-bundle.html").read_text(encoding="utf-8").lower()


def test_release_validation_and_maturity() -> None:
    validation = run_cli("validate-release", "--root", str(ROOT))
    assert validation.returncode == 0, validation.stdout + validation.stderr
    payload = json.loads(validation.stdout)
    assert payload["status"] == "pass"

    maturity = run_cli("maturity-report", "--root", str(ROOT))
    assert maturity.returncode == 0
    assert json.loads(maturity.stdout)["score"] >= 90


def test_fixture_doctor_reports_json_and_markdown(tmp_path: Path) -> None:
    out = tmp_path / "demo"
    result = run_cli(
        "fixture-doctor",
        "--fixtures",
        str(ROOT / "examples"),
        "--policy",
        str(ROOT / "examples" / "review-policy.json"),
        "--output",
        str(out),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads((out / "fixture-doctor.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == "valuation-scenario-lab.fixture-doctor.v0.5"
    assert payload["status"] == "pass"
    assert payload["issue_count"] == 0
    assert "No buy/sell/hold advice." in (out / "fixture-doctor.md").read_text(encoding="utf-8")

    markdown = run_cli(
        "fixture-doctor",
        "--fixtures",
        str(ROOT / "examples"),
        "--policy",
        str(ROOT / "examples" / "review-policy.json"),
        "--format",
        "markdown",
    )
    assert markdown.returncode == 0
    assert "# Fixture Doctor" in markdown.stdout


def test_fixture_doctor_flags_malformed_fixtures(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "bad.json").write_text(
        json.dumps(
            {
                "company": "Broken Fixture",
                "current_price": "forty",
                "shares_outstanding_m": 10,
                "net_cash_m": 1,
                "source_freshness": [{"name": "old memo", "age_days": 99}],
                "scenarios": [
                    {
                        "name": "Bad case",
                        "weight": 0.7,
                        "starting_revenue_m": 100,
                        "revenue_growth_pct": "fast",
                        "fcf_margin_pct": 12,
                        "discount_rate_pct": 10,
                        "terminal_growth_pct": 3,
                        "terminal_multiple": 14,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    result = run_cli("fixture-doctor", "--fixtures", str(fixtures))
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    categories = {item["category"] for item in payload["issues"]}
    assert {"numeric", "weight", "staleness"} <= categories
    assert payload["status"] == "fail"


def test_build_packet_rejects_malformed_fixture(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "company.json").write_text(
        json.dumps(
            {
                "company": "Broken Fixture",
                "current_price": 10,
                "shares_outstanding_m": 1,
                "net_cash_m": 0,
                "scenarios": [],
            }
        ),
        encoding="utf-8",
    )
    result = run_cli("build-packet", "--fixtures", str(fixtures), "--output", str(tmp_path / "demo"))
    assert result.returncode == 1
    assert "scenarios must be a non-empty list" in result.stderr


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
    assert quickstart_payload["schema_version"] == "valuation-scenario-lab.quickstart-check.v0.5"
    assert (out / "quickstart-check.md").exists()
    assert (out / "fixture-doctor.md").exists()
    assert (out / "decision-journal.md").exists()
    assert (out / "assumption-change-walkthrough.md").exists()
    assert (out / "multi-company-demo-gallery.html").exists()
    assert (out / "public-readiness-landing.html").exists()
    assert (out / "showcase-dashboard.svg").exists()
    assert (out / "showcase-dashboard.html").exists()
    assert (out / "thesis-brief.md").exists()
    assert (out / "thesis-brief.html").exists()
    assert (out / "scenario-library.md").exists()
    assert (out / "scenario-library.html").exists()
    assert (out / "sample-workflow.md").exists()
    assert (out / "sample-workflow.html").exists()
    assert (out / "reproducibility-audit.md").exists()
    assert (out / "reproducibility-audit.html").exists()

    receipt = run_cli("visual-receipt", "--root", str(ROOT), "--output", str(out))
    assert receipt.returncode == 0, receipt.stdout + receipt.stderr
    receipt_payload = json.loads((out / "visual-receipt.json").read_text(encoding="utf-8"))
    assert receipt_payload["schema_version"] == "valuation-scenario-lab.visual-receipt.v0.5"
    assert receipt_payload["artifact_count"] == 38
    assert "No buy/sell/hold advice." in (out / "visual-receipt.html").read_text(encoding="utf-8")


def test_key_demo_outputs_match_golden_snapshot(tmp_path: Path) -> None:
    out = tmp_path / "demo"
    result = run_cli("quickstart-check", "--root", str(ROOT), "--output", str(out))
    assert result.returncode == 0, result.stdout + result.stderr
    assert key_demo_snapshot(out) == golden_snapshot("key-demo-snapshots.json")
