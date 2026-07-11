from __future__ import annotations

import argparse
import json
import html
import sys
import sysconfig
import tempfile
from pathlib import Path
from typing import Any

from . import __version__
from .doctor import fixture_doctor, fixture_doctor_markdown
from .engine import (
    assumption_change_walkthrough,
    build_thesis_brief,
    build_decision_journal,
    build_packet,
    build_review_ledger,
    compare_packets,
    demo_gallery,
    scenario_library,
    sensitivity_matrix,
    validate_company,
)
from .io import ensure_dir, read_json, write_json, write_text
from .release import maturity_report as maturity_payload
from .release import reproducibility_audit as reproducibility_audit_payload
from .release import release_manifest as manifest_payload
from .release import export_bundle_manifest as export_bundle_payload
from .release import install_smoke_receipt as install_smoke_payload
from .release import validate_release as validate_release_payload
from .release import safety_boundary_checks, schema_version_checks
from .render import packet_html, packet_markdown, simple_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="valuation-scenario-lab")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build-packet")
    build.add_argument("--fixtures", default="examples")
    build.add_argument("--output", default="demo")

    hist = sub.add_parser("compare-history")
    hist.add_argument("--current", default="demo/valuation-packet.json")
    hist.add_argument("--prior", default="examples/prior-packet.json")
    hist.add_argument("--output", default="demo")

    ledger = sub.add_parser("review-ledger")
    ledger.add_argument("--packet", default="demo/valuation-packet.json")
    ledger.add_argument("--policy", default="examples/review-policy.json")
    ledger.add_argument("--output", default="demo")

    matrix = sub.add_parser("sensitivity-matrix")
    matrix.add_argument("--fixtures", default="examples")
    matrix.add_argument("--output", default="demo")

    walkthrough = sub.add_parser("assumption-change-walkthrough")
    walkthrough.add_argument("--fixtures", default="examples")
    walkthrough.add_argument("--output", default="demo")
    walkthrough.add_argument("--scenario", default=None)
    walkthrough.add_argument("--field", default="fcf_margin_pct")
    walkthrough.add_argument("--delta", type=float, default=2.0)

    gallery = sub.add_parser("demo-gallery")
    gallery.add_argument("--fixtures", default="examples")
    gallery.add_argument("--output", default="demo")

    journal = sub.add_parser("decision-journal")
    journal.add_argument("--packet", default="demo/valuation-packet.json")
    journal.add_argument("--ledger", default="demo/review-ledger.json")
    journal.add_argument("--output", default="demo")

    landing = sub.add_parser("public-readiness-landing")
    landing.add_argument("--root", default=".")
    landing.add_argument("--output", default="demo")

    selfcheck = sub.add_parser("selfcheck")
    selfcheck.add_argument("--root", default=None)

    quickstart = sub.add_parser("quickstart-check")
    quickstart.add_argument("--root", default=".")
    quickstart.add_argument("--output", default="demo")

    doctor = sub.add_parser("fixture-doctor")
    doctor.add_argument("--fixtures", default="examples")
    doctor.add_argument("--policy", default=None)
    doctor.add_argument("--format", choices=["json", "markdown"], default="json")
    doctor.add_argument("--output", default=None)

    receipt = sub.add_parser("visual-receipt")
    receipt.add_argument("--root", default=".")
    receipt.add_argument("--output", default="demo")

    showcase = sub.add_parser("showcase-dashboard")
    showcase.add_argument("--root", default=".")
    showcase.add_argument("--output", default="demo")

    thesis = sub.add_parser("thesis-brief")
    thesis.add_argument("--root", default=".")
    thesis.add_argument("--output", default="demo")

    library = sub.add_parser("scenario-library")
    library.add_argument("--fixtures", default="examples")
    library.add_argument("--output", default="demo")

    validate = sub.add_parser("validate-release")
    validate.add_argument("--root", default=".")
    validate.add_argument("--format", choices=["json", "markdown"], default="json")

    maturity = sub.add_parser("maturity-report")
    maturity.add_argument("--root", default=".")
    maturity.add_argument("--format", choices=["json", "markdown"], default="json")

    manifest = sub.add_parser("release-manifest")
    manifest.add_argument("--root", default=".")
    manifest.add_argument("--output", default="release")

    bundle = sub.add_parser("export-bundle")
    bundle.add_argument("--root", default=".")
    bundle.add_argument("--output", default="release")

    smoke = sub.add_parser("install-smoke-receipt")
    smoke.add_argument("--root", default=".")
    smoke.add_argument("--output", default="release")

    audit = sub.add_parser("reproducibility-audit")
    audit.add_argument("--root", default=".")
    audit.add_argument("--output", default="demo")

    workflow = sub.add_parser("sample-workflow")
    workflow.add_argument("--root", default=".")
    workflow.add_argument("--output", default="demo")

    template = sub.add_parser("new-fixture-template")
    template.add_argument("--output", default="demo/onboarding-template")

    casebook = sub.add_parser("casebook")
    casebook.add_argument("--root", default=".")
    casebook.add_argument("--output", default="demo")

    scorecard = sub.add_parser("reviewer-scorecard")
    scorecard.add_argument("--root", default=".")
    scorecard.add_argument("--output", default="demo")

    troubleshoot = sub.add_parser("troubleshoot")
    troubleshoot.add_argument("--root", default=".")
    troubleshoot.add_argument("--output", default="demo")

    snippet = sub.add_parser("readme-snippet")
    snippet.add_argument("--root", default=".")
    snippet.add_argument("--output", default="demo")

    deck = sub.add_parser("release-deck")
    deck.add_argument("--root", default=".")
    deck.add_argument("--output", default="demo")

    demo = sub.add_parser("demo")
    demo.add_argument("--root", default=".")

    args = parser.parse_args(argv)
    try:
        if args.command == "build-packet":
            return command_build_packet(Path(args.fixtures), Path(args.output))
        if args.command == "compare-history":
            return command_compare_history(Path(args.current), Path(args.prior), Path(args.output))
        if args.command == "review-ledger":
            return command_review_ledger(Path(args.packet), Path(args.policy), Path(args.output))
        if args.command == "sensitivity-matrix":
            return command_sensitivity(Path(args.fixtures), Path(args.output))
        if args.command == "assumption-change-walkthrough":
            return command_assumption_walkthrough(Path(args.fixtures), Path(args.output), args.scenario, args.field, args.delta)
        if args.command == "demo-gallery":
            return command_demo_gallery(Path(args.fixtures), Path(args.output))
        if args.command == "decision-journal":
            return command_decision_journal(Path(args.packet), Path(args.ledger), Path(args.output))
        if args.command == "public-readiness-landing":
            return command_public_readiness_landing(Path(args.root), Path(args.output))
        if args.command == "selfcheck":
            return command_selfcheck(Path(args.root) if args.root else None)
        if args.command == "quickstart-check":
            return command_quickstart_check(Path(args.root), Path(args.output))
        if args.command == "fixture-doctor":
            return command_fixture_doctor(
                Path(args.fixtures),
                Path(args.policy) if args.policy else None,
                args.format,
                Path(args.output) if args.output else None,
            )
        if args.command == "visual-receipt":
            return command_visual_receipt(Path(args.root), Path(args.output))
        if args.command == "showcase-dashboard":
            return command_showcase_dashboard(Path(args.root), Path(args.output))
        if args.command == "thesis-brief":
            return command_thesis_brief(Path(args.root), Path(args.output))
        if args.command == "scenario-library":
            return command_scenario_library(Path(args.fixtures), Path(args.output))
        if args.command == "validate-release":
            return emit_validation(validate_release_payload(Path(args.root)), args.format)
        if args.command == "maturity-report":
            return emit_validation(maturity_payload(Path(args.root)), args.format)
        if args.command == "release-manifest":
            return command_manifest(Path(args.root), Path(args.output))
        if args.command == "export-bundle":
            return command_export_bundle(Path(args.root), Path(args.output))
        if args.command == "install-smoke-receipt":
            return command_install_smoke_receipt(Path(args.root), Path(args.output))
        if args.command == "reproducibility-audit":
            return command_reproducibility_audit(Path(args.root), Path(args.output))
        if args.command == "sample-workflow":
            return command_sample_workflow(Path(args.root), Path(args.output))
        if args.command == "new-fixture-template":
            return command_new_fixture_template(Path(args.output))
        if args.command == "casebook":
            return command_casebook(Path(args.root), Path(args.output))
        if args.command == "reviewer-scorecard":
            return command_reviewer_scorecard(Path(args.root), Path(args.output))
        if args.command == "troubleshoot":
            return command_troubleshoot(Path(args.root), Path(args.output))
        if args.command == "readme-snippet":
            return command_readme_snippet(Path(args.root), Path(args.output))
        if args.command == "release-deck":
            return command_release_deck(Path(args.root), Path(args.output))
        if args.command == "demo":
            root = Path(args.root)
            command_build_packet(root / "examples", root / "demo")
            command_compare_history(root / "demo" / "valuation-packet.json", root / "examples" / "prior-packet.json", root / "demo")
            command_review_ledger(root / "demo" / "valuation-packet.json", root / "examples" / "review-policy.json", root / "demo")
            command_sensitivity(root / "examples", root / "demo")
            command_assumption_walkthrough(root / "examples", root / "demo", None, "fcf_margin_pct", 2.0)
            command_demo_gallery(root / "examples", root / "demo")
            command_decision_journal(root / "demo" / "valuation-packet.json", root / "demo" / "review-ledger.json", root / "demo")
            command_public_readiness_landing(root, root / "demo")
            command_fixture_doctor(root / "examples", root / "examples" / "review-policy.json", "json", root / "demo")
            command_quickstart_check(root, root / "demo")
            command_visual_receipt(root, root / "demo")
            command_showcase_dashboard(root, root / "demo")
            command_thesis_brief(root, root / "demo")
            command_scenario_library(root / "examples", root / "demo")
            command_sample_workflow(root, root / "demo")
            command_reproducibility_audit(root, root / "demo")
            command_new_fixture_template(root / "demo" / "onboarding-template")
            command_casebook(root, root / "demo")
            command_reviewer_scorecard(root, root / "demo")
            command_troubleshoot(root, root / "demo")
            command_readme_snippet(root, root / "demo")
            command_release_deck(root, root / "demo")
            command_install_smoke_receipt(root, root / "release")
            command_manifest(root, root / "release")
            command_export_bundle(root, root / "release")
            return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 1


def command_build_packet(fixtures: Path, output: Path) -> int:
    packet = build_packet(read_json(fixtures / "company.json"))
    ensure_dir(output)
    write_json(output / "valuation-packet.json", packet)
    write_text(output / "valuation-packet.md", packet_markdown(packet))
    write_text(output / "valuation-packet.html", packet_html(packet))
    print(f"wrote {output / 'valuation-packet.json'}")
    return 0


def command_compare_history(current: Path, prior: Path, output: Path) -> int:
    payload = compare_packets(read_json(current), read_json(prior))
    ensure_dir(output)
    write_json(output / "compare-history.json", payload)
    write_text(output / "compare-history.md", simple_markdown("Valuation History Comparison", payload))
    print(f"wrote {output / 'compare-history.json'}")
    return 0


def command_review_ledger(packet: Path, policy: Path, output: Path) -> int:
    payload = build_review_ledger(read_json(packet), read_json(policy) if policy.exists() else None)
    ensure_dir(output)
    write_json(output / "review-ledger.json", payload)
    write_text(output / "review-ledger.md", simple_markdown("Valuation Review Ledger", payload))
    print(f"wrote {output / 'review-ledger.json'}")
    return 0


def command_sensitivity(fixtures: Path, output: Path) -> int:
    payload = sensitivity_matrix(read_json(fixtures / "company.json"))
    ensure_dir(output)
    write_json(output / "sensitivity-matrix.json", payload)
    write_text(output / "sensitivity-matrix.md", simple_markdown("Valuation Sensitivity Matrix", payload))
    print(f"wrote {output / 'sensitivity-matrix.json'}")
    return 0


def command_assumption_walkthrough(fixtures: Path, output: Path, scenario: str | None, field: str, delta: float) -> int:
    payload = assumption_change_walkthrough(read_json(fixtures / "company.json"), scenario, field, delta)
    ensure_dir(output)
    write_json(output / "assumption-change-walkthrough.json", payload)
    write_text(output / "assumption-change-walkthrough.md", assumption_walkthrough_markdown(payload))
    write_text(output / "assumption-change-walkthrough.html", assumption_walkthrough_html(payload))
    print(f"wrote {output / 'assumption-change-walkthrough.json'}")
    return 0


def command_demo_gallery(fixtures: Path, output: Path) -> int:
    companies = fixture_companies(fixtures)
    payload = demo_gallery(companies)
    ensure_dir(output)
    write_json(output / "multi-company-demo-gallery.json", payload)
    write_text(output / "multi-company-demo-gallery.md", demo_gallery_markdown(payload))
    write_text(output / "multi-company-demo-gallery.html", demo_gallery_html(payload))
    print(f"wrote {output / 'multi-company-demo-gallery.json'}")
    return 0


def command_decision_journal(packet: Path, ledger: Path, output: Path) -> int:
    payload = build_decision_journal(read_json(packet), read_json(ledger) if ledger.exists() else None)
    ensure_dir(output)
    write_json(output / "decision-journal.json", payload)
    write_text(output / "decision-journal.md", decision_journal_markdown(payload))
    print(f"wrote {output / 'decision-journal.json'}")
    return 0


def command_public_readiness_landing(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_demo_artifacts(root, output)
    command_thesis_brief(root, output)
    command_scenario_library(root / "examples", output)
    packet = read_json(output / "valuation-packet.json")
    payload = public_readiness_payload(packet)
    write_json(output / "public-readiness-landing.json", payload)
    write_text(output / "public-readiness-landing.md", public_readiness_markdown(payload))
    write_text(output / "public-readiness-landing.html", public_readiness_html(payload))
    print(f"wrote {output / 'public-readiness-landing.html'}")
    return 0


def command_selfcheck(root_arg: Path | None = None) -> int:
    root = resolve_root(root_arg)
    doctor = fixture_doctor(root / "examples", read_json(root / "examples" / "review-policy.json"))
    if doctor["status"] != "pass":
        for item in doctor["issues"]:
            if item["severity"] == "error":
                print(f"FAIL {item['category']} {item['file']} {item['path']}: {item['message']}")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        command_build_packet(root / "examples", out)
        command_compare_history(out / "valuation-packet.json", root / "examples" / "prior-packet.json", out)
        command_review_ledger(out / "valuation-packet.json", root / "examples" / "review-policy.json", out)
        command_sensitivity(root / "examples", out)
        command_assumption_walkthrough(root / "examples", out, None, "fcf_margin_pct", 2.0)
        command_demo_gallery(root / "examples", out)
        command_decision_journal(out / "valuation-packet.json", out / "review-ledger.json", out)
        command_public_readiness_landing(root, out)
        command_fixture_doctor(root / "examples", root / "examples" / "review-policy.json", "json", out)
        command_showcase_dashboard(root, out)
        command_thesis_brief(root, out)
        command_scenario_library(root / "examples", out)
        command_sample_workflow(root, out)
        command_reproducibility_audit(root, out)
        command_new_fixture_template(out / "onboarding-template")
        command_casebook(root, out)
        command_reviewer_scorecard(root, out)
        command_troubleshoot(root, out)
        command_readme_snippet(root, out)
        command_release_deck(root, out)
        command_install_smoke_receipt(root, out / "release")
        command_manifest(root, out / "release")
        command_export_bundle(root, out / "release")
    validation = validate_release_payload(root)
    if validation["status"] != "pass":
        print("FAIL release validation")
        for item in validation["findings"]:
            print(f"{item['severity'].upper()} {item['message']}")
        return 1
    print("selfcheck passed")
    return 0


def command_quickstart_check(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_demo_artifacts(root, output)
    command_public_readiness_landing(root, output)
    command_fixture_doctor(root / "examples", root / "examples" / "review-policy.json", "json", output)
    command_showcase_dashboard(root, output)
    command_thesis_brief(root, output)
    command_scenario_library(root / "examples", output)
    command_sample_workflow(root, output)
    command_new_fixture_template(output / "onboarding-template")
    command_casebook(root, output)
    command_reviewer_scorecard(root, output)
    command_troubleshoot(root, output)
    command_readme_snippet(root, output)
    command_release_deck(root, output)
    expected = [
        "valuation-packet.json",
        "valuation-packet.md",
        "valuation-packet.html",
        "compare-history.json",
        "compare-history.md",
        "review-ledger.json",
        "review-ledger.md",
        "sensitivity-matrix.json",
        "sensitivity-matrix.md",
        "assumption-change-walkthrough.json",
        "assumption-change-walkthrough.md",
        "assumption-change-walkthrough.html",
        "multi-company-demo-gallery.json",
        "multi-company-demo-gallery.md",
        "multi-company-demo-gallery.html",
        "decision-journal.json",
        "decision-journal.md",
        "public-readiness-landing.json",
        "public-readiness-landing.md",
        "public-readiness-landing.html",
        "fixture-doctor.json",
        "fixture-doctor.md",
        "showcase-dashboard.json",
        "showcase-dashboard.svg",
        "showcase-dashboard.md",
        "showcase-dashboard.html",
        "thesis-brief.json",
        "thesis-brief.md",
        "thesis-brief.html",
        "scenario-library.json",
        "scenario-library.md",
        "scenario-library.html",
        "reproducibility-audit.json",
        "reproducibility-audit.md",
        "reproducibility-audit.html",
        "sample-workflow.json",
        "sample-workflow.md",
        "sample-workflow.html",
        "casebook.json",
        "casebook.md",
        "casebook.html",
        "reviewer-scorecard.json",
        "reviewer-scorecard.md",
        "reviewer-scorecard.html",
        "troubleshoot.json",
        "troubleshoot.md",
        "troubleshoot.html",
        "readme-snippet.json",
        "readme-snippet.md",
        "readme-snippet.html",
        "release-deck.json",
        "release-deck.md",
        "release-deck.html",
        "onboarding-template/README.md",
        "onboarding-template/company.json",
        "onboarding-template/review-policy.json",
        "onboarding-template/prior-packet.json",
    ]
    files = [{"path": f"demo/{name}", "exists": (output / name).exists()} for name in expected]
    payload = {
        "schema_version": "valuation-scenario-lab.quickstart-check.v0.5",
        "status": "pass" if all(item["exists"] for item in files) else "fail",
        "fixture_source": "local-or-packaged-fixtures",
        "commands": [
            "valuation-scenario-lab demo",
            "valuation-scenario-lab selfcheck --root .",
            "valuation-scenario-lab quickstart-check --root . --output demo",
            "valuation-scenario-lab visual-receipt --root . --output demo",
            "valuation-scenario-lab showcase-dashboard --root . --output demo",
            "valuation-scenario-lab thesis-brief --root . --output demo",
            "valuation-scenario-lab scenario-library --fixtures examples --output demo",
            "valuation-scenario-lab sample-workflow --root . --output demo",
            "valuation-scenario-lab reproducibility-audit --root . --output demo",
            "valuation-scenario-lab new-fixture-template --output demo/onboarding-template",
            "valuation-scenario-lab casebook --root . --output demo",
            "valuation-scenario-lab reviewer-scorecard --root . --output demo",
            "valuation-scenario-lab troubleshoot --root . --output demo",
            "valuation-scenario-lab readme-snippet --root . --output demo",
            "valuation-scenario-lab release-deck --root . --output demo",
            "valuation-scenario-lab fixture-doctor --fixtures examples --policy examples/review-policy.json --format markdown --output demo",
            "valuation-scenario-lab assumption-change-walkthrough --fixtures examples --output demo",
            "valuation-scenario-lab demo-gallery --fixtures examples --output demo",
            "valuation-scenario-lab decision-journal --packet demo/valuation-packet.json --ledger demo/review-ledger.json --output demo",
            "valuation-scenario-lab public-readiness-landing --root . --output demo",
            "valuation-scenario-lab install-smoke-receipt --root . --output release",
            "valuation-scenario-lab release-manifest --root . --output release",
            "valuation-scenario-lab export-bundle --root . --output release",
        ],
        "files": files,
        "boundaries": [
            "No live data.",
            "No broker connections.",
            "No buy/sell/hold advice.",
        ],
    }
    write_json(output / "quickstart-check.json", payload)
    write_text(output / "quickstart-check.md", quickstart_markdown(payload))
    command_reproducibility_audit(root, output)
    files = [{"path": f"demo/{name}", "exists": (output / name).exists()} for name in expected]
    payload["status"] = "pass" if all(item["exists"] for item in files) else "fail"
    payload["files"] = files
    write_json(output / "quickstart-check.json", payload)
    write_text(output / "quickstart-check.md", quickstart_markdown(payload))
    print(f"wrote {output / 'quickstart-check.json'}")
    return 0 if payload["status"] == "pass" else 1


def command_visual_receipt(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_demo_artifacts(root, output)
    packet = read_json(output / "valuation-packet.json")
    payload = {
        "schema_version": "valuation-scenario-lab.visual-receipt.v0.5",
        "company": packet["company"],
        "ticker": packet["ticker"],
        "weighted_fair_value_per_share": packet["weighted_fair_value_per_share"],
        "weighted_range_per_share": packet["weighted_range_per_share"],
        "margin_of_safety_label": packet["margin_of_safety_label"],
        "weighted_margin_of_safety_pct": packet["weighted_margin_of_safety_pct"],
        "artifact_count": 50,
        "boundaries": packet["boundaries"],
    }
    write_json(output / "visual-receipt.json", payload)
    write_text(output / "visual-receipt.md", visual_receipt_markdown(payload))
    write_text(output / "visual-receipt.html", visual_receipt_html(payload))
    print(f"wrote {output / 'visual-receipt.html'}")
    return 0


def command_showcase_dashboard(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_demo_artifacts(root, output)
    command_fixture_doctor(root / "examples", root / "examples" / "review-policy.json", "json", output)
    packet = read_json(output / "valuation-packet.json")
    gallery = read_json(output / "multi-company-demo-gallery.json")
    doctor = read_json(output / "fixture-doctor.json")
    matrix = read_json(output / "sensitivity-matrix.json")
    payload = showcase_payload(packet, gallery, doctor, matrix)
    write_json(output / "showcase-dashboard.json", payload)
    write_text(output / "showcase-dashboard.svg", showcase_svg(payload))
    write_text(output / "showcase-dashboard.md", showcase_markdown(payload))
    write_text(output / "showcase-dashboard.html", showcase_html(payload))
    print(f"wrote {output / 'showcase-dashboard.svg'}")
    return 0


def command_thesis_brief(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_demo_artifacts(root, output)
    command_fixture_doctor(root / "examples", root / "examples" / "review-policy.json", "json", output)
    command_showcase_dashboard(root, output)
    payload = build_thesis_brief(
        read_json(output / "valuation-packet.json"),
        read_json(output / "compare-history.json"),
        read_json(output / "decision-journal.json"),
        read_json(output / "fixture-doctor.json"),
        read_json(output / "showcase-dashboard.json"),
    )
    write_json(output / "thesis-brief.json", payload)
    write_text(output / "thesis-brief.md", thesis_brief_markdown(payload))
    write_text(output / "thesis-brief.html", thesis_brief_html(payload))
    print(f"wrote {output / 'thesis-brief.json'}")
    return 0


def command_scenario_library(fixtures: Path, output: Path) -> int:
    payload = scenario_library(fixture_companies(fixtures))
    ensure_dir(output)
    write_json(output / "scenario-library.json", payload)
    write_text(output / "scenario-library.md", scenario_library_markdown(payload))
    write_text(output / "scenario-library.html", scenario_library_html(payload))
    print(f"wrote {output / 'scenario-library.json'}")
    return 0


def command_reproducibility_audit(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_dir(output)
    generated = [
        relative_output(root, output / "reproducibility-audit.json"),
        relative_output(root, output / "reproducibility-audit.md"),
        relative_output(root, output / "reproducibility-audit.html"),
    ]
    payload = reproducibility_audit_payload(root, generated)
    write_json(output / "reproducibility-audit.json", payload)
    write_text(output / "reproducibility-audit.md", reproducibility_audit_markdown(payload))
    write_text(output / "reproducibility-audit.html", reproducibility_audit_html(payload))
    print(f"wrote {output / 'reproducibility-audit.json'}")
    return 0 if payload["status"] == "pass" else 1


def command_sample_workflow(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_dir(output)
    payload = sample_workflow_payload(root)
    write_json(output / "sample-workflow.json", payload)
    write_text(output / "sample-workflow.md", sample_workflow_markdown(payload))
    write_text(output / "sample-workflow.html", sample_workflow_html(payload))
    print(f"wrote {output / 'sample-workflow.json'}")
    return 0 if payload["status"] == "pass" else 1


def command_new_fixture_template(output: Path) -> int:
    ensure_dir(output)
    company = onboarding_company_template()
    prior_packet = build_packet(company)
    prior_packet["schema_version"] = "valuation-scenario-lab.prior-packet-template.v0.9"
    prior_packet["generated_on"] = "static-local-template"
    prior_packet["template_note"] = "Fictional prior packet scaffold; replace values with local research before use."
    write_json(output / "company.json", company)
    write_json(output / "review-policy.json", onboarding_review_policy_template())
    write_json(output / "prior-packet.json", prior_packet)
    write_text(output / "README.md", onboarding_template_readme())
    print(f"wrote {output / 'company.json'}")
    return 0


def command_casebook(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_dir(output)
    ensure_demo_artifacts(root, output)
    command_thesis_brief(root, output)
    command_scenario_library(root / "examples", output)
    command_sample_workflow(root, output)
    audit = read_json(output / "reproducibility-audit.json") if (output / "reproducibility-audit.json").exists() else {
        "status": "pending",
        "boundaries": ["No live data.", "No broker connections.", "No buy/sell/hold advice."],
    }
    payload = casebook_payload(
        read_json(output / "valuation-packet.json"),
        read_json(output / "scenario-library.json"),
        read_json(output / "thesis-brief.json"),
        read_json(output / "sample-workflow.json"),
        audit,
    )
    write_json(output / "casebook.json", payload)
    write_text(output / "casebook.md", casebook_markdown(payload))
    write_text(output / "casebook.html", casebook_html(payload))
    command_reproducibility_audit(root, output)
    payload = casebook_payload(
        read_json(output / "valuation-packet.json"),
        read_json(output / "scenario-library.json"),
        read_json(output / "thesis-brief.json"),
        read_json(output / "sample-workflow.json"),
        read_json(output / "reproducibility-audit.json"),
    )
    write_json(output / "casebook.json", payload)
    write_text(output / "casebook.md", casebook_markdown(payload))
    write_text(output / "casebook.html", casebook_html(payload))
    print(f"wrote {output / 'casebook.html'}")
    return 0


def command_reviewer_scorecard(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_dir(output)
    ensure_demo_artifacts(root, output)
    command_fixture_doctor(root / "examples", root / "examples" / "review-policy.json", "json", output)
    command_showcase_dashboard(root, output)
    command_visual_receipt(root, output)
    command_sample_workflow(root, output)
    payload = reviewer_scorecard_payload(root, output)
    write_json(output / "reviewer-scorecard.json", payload)
    write_text(output / "reviewer-scorecard.md", reviewer_scorecard_markdown(payload))
    write_text(output / "reviewer-scorecard.html", reviewer_scorecard_html(payload))
    print(f"wrote {output / 'reviewer-scorecard.json'}")
    return 0 if payload["status"] in {"strong", "reviewable"} else 1


def command_troubleshoot(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_dir(output)
    payload = troubleshoot_payload(root)
    write_json(output / "troubleshoot.json", payload)
    write_text(output / "troubleshoot.md", troubleshoot_markdown(payload))
    write_text(output / "troubleshoot.html", troubleshoot_html(payload))
    print(f"wrote {output / 'troubleshoot.json'}")
    return 0


def command_readme_snippet(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_dir(output)
    ensure_demo_artifacts(root, output)
    payload = readme_snippet_payload(root, output)
    write_json(output / "readme-snippet.json", payload)
    write_text(output / "readme-snippet.md", readme_snippet_markdown(payload))
    write_text(output / "readme-snippet.html", readme_snippet_html(payload))
    print(f"wrote {output / 'readme-snippet.json'}")
    return 0


def command_release_deck(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_dir(output)
    ensure_demo_artifacts(root, output)
    command_readme_snippet(root, output)
    command_reviewer_scorecard(root, output)
    payload = release_deck_payload(root, output)
    write_json(output / "release-deck.json", payload)
    write_text(output / "release-deck.md", release_deck_markdown(payload))
    write_text(output / "release-deck.html", release_deck_html(payload))
    print(f"wrote {output / 'release-deck.json'}")
    return 0


def ensure_demo_artifacts(root: Path, output: Path) -> None:
    command_build_packet(root / "examples", output)
    command_compare_history(output / "valuation-packet.json", root / "examples" / "prior-packet.json", output)
    command_review_ledger(output / "valuation-packet.json", root / "examples" / "review-policy.json", output)
    command_sensitivity(root / "examples", output)
    command_assumption_walkthrough(root / "examples", output, None, "fcf_margin_pct", 2.0)
    command_demo_gallery(root / "examples", output)
    command_decision_journal(output / "valuation-packet.json", output / "review-ledger.json", output)


def onboarding_company_template() -> dict[str, Any]:
    return {
        "company": "Northstar Kitchens Collective",
        "ticker": "NSKC",
        "currency": "USD",
        "template_note": "Fictional onboarding fixture for local research practice only.",
        "current_price": 24.5,
        "shares_outstanding_m": 88.0,
        "net_cash_m": 95.0,
        "source_freshness": [
            {"name": "fictional annual operating memo", "age_days": 14},
            {"name": "fictional segment margin review", "age_days": 21},
        ],
        "scenarios": [
            {
                "name": "Base store refresh case",
                "weight": 0.55,
                "starting_revenue_m": 760.0,
                "revenue_growth_pct": 5.5,
                "fcf_margin_pct": 9.5,
                "discount_rate_pct": 10.5,
                "terminal_growth_pct": 2.5,
                "terminal_multiple": 13.0,
                "catalysts": ["store refresh cadence", "private-label mix"],
                "risks": ["freight inflation", "regional demand softness"],
                "source_freshness": [{"name": "fictional base scenario memo", "age_days": 18}],
            },
            {
                "name": "Traffic pressure case",
                "weight": 0.25,
                "starting_revenue_m": 730.0,
                "revenue_growth_pct": 1.5,
                "fcf_margin_pct": 7.0,
                "discount_rate_pct": 12.0,
                "terminal_growth_pct": 1.5,
                "terminal_multiple": 10.0,
                "catalysts": ["inventory discipline"],
                "risks": ["lower foot traffic", "markdown pressure"],
                "source_freshness": [{"name": "fictional downside memo", "age_days": 24}],
            },
            {
                "name": "Channel expansion case",
                "weight": 0.20,
                "starting_revenue_m": 790.0,
                "revenue_growth_pct": 8.0,
                "fcf_margin_pct": 11.5,
                "discount_rate_pct": 10.0,
                "terminal_growth_pct": 3.0,
                "terminal_multiple": 15.0,
                "catalysts": ["commercial channel expansion", "loyalty conversion"],
                "risks": ["execution delay"],
                "source_freshness": [{"name": "fictional upside memo", "age_days": 12}],
            },
        ],
    }


def onboarding_review_policy_template() -> dict[str, Any]:
    return {
        "high_priority_abs_mos_pct": 20,
        "owner_placeholder": "research reviewer",
        "freshness_limit_days": 45,
        "template_note": "Edit owner and freshness rules for local review cadence; do not add broker or account data.",
        "boundaries": [
            "No live data.",
            "No broker connections.",
            "No buy/sell/hold advice.",
        ],
    }


def onboarding_template_readme() -> str:
    return """# New Fixture Template

This directory is a fictional onboarding scaffold for building a local valuation scenario fixture.

Files:

- `company.json`: fictional company assumptions with three weighted scenarios.
- `review-policy.json`: local review thresholds and freshness policy.
- `prior-packet.json`: deterministic prior packet template for `compare-history`.

Replace the fictional values with documented local research notes before publishing outputs. Keep all inputs static and local.

Boundaries:

- No live data.
- No broker connections.
- No buy/sell/hold advice.
"""


def command_fixture_doctor(fixtures: Path, policy: Path | None, fmt: str, output: Path | None) -> int:
    policy_payload = read_json(policy) if policy and policy.exists() else None
    payload = fixture_doctor(fixtures, policy_payload)
    markdown = fixture_doctor_markdown(payload)
    if output is not None:
        ensure_dir(output)
        write_json(output / "fixture-doctor.json", payload)
        write_text(output / "fixture-doctor.md", markdown)
        print(f"wrote {output / 'fixture-doctor.json'}")
    elif fmt == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(markdown)
    return 0 if payload["status"] == "pass" else 1


def fixture_companies(fixtures: Path) -> list[dict]:
    companies = []
    for path in sorted(fixtures.glob("*.json")):
        if path.name in {"prior-packet.json", "review-policy.json"}:
            continue
        payload = read_json(path)
        if not validate_company(payload):
            companies.append(payload)
    if not companies:
        raise ValueError(f"no valid company fixtures found in {fixtures}")
    return companies


def resolve_root(root_arg: Path | None) -> Path:
    candidates = []
    if root_arg is not None:
        candidates.append(root_arg)
    candidates.append(Path.cwd())
    candidates.extend(installed_data_roots())
    for candidate in candidates:
        root = candidate.resolve()
        if (root / "examples" / "company.json").exists():
            return root
    checked = ", ".join(str(item) for item in candidates)
    raise FileNotFoundError(f"could not find examples/company.json; checked {checked}")


def installed_data_roots() -> list[Path]:
    roots = []
    for key in ["data", "platdata"]:
        try:
            base = sysconfig.get_path(key)
        except KeyError:
            base = None
        if base:
            roots.append(Path(base) / "share" / "valuation-scenario-lab")
    prefix = sysconfig.get_config_var("prefix")
    if prefix:
        roots.append(Path(str(prefix)) / "share" / "valuation-scenario-lab")
    return roots


def quickstart_markdown(payload: dict) -> str:
    lines = ["# Quickstart Check", "", f"Status: {payload['status']}", "", "## Commands", ""]
    lines.extend(f"- `{item}`" for item in payload["commands"])
    lines.extend(["", "## Files", ""])
    lines.extend(f"- `{item['path']}`: {'ok' if item['exists'] else 'missing'}" for item in payload["files"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def visual_receipt_markdown(payload: dict) -> str:
    return f"""# Visual Receipt

Company: {payload['company']} ({payload['ticker']})

Weighted fair value per share: {payload['weighted_fair_value_per_share']:.2f}
Weighted range per share: {payload['weighted_range_per_share'][0]:.2f} to {payload['weighted_range_per_share'][1]:.2f}
Margin-of-safety label: {payload['margin_of_safety_label']} ({payload['weighted_margin_of_safety_pct']:.1f}%)
Artifact count: {payload['artifact_count']}

## Boundaries

{chr(10).join(f"- {item}" for item in payload["boundaries"])}
"""


def visual_receipt_html(payload: dict) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Valuation Scenario Lab Visual Receipt</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
.metric {{ border: 1px solid #ccd1d1; display: inline-block; margin: 0.25rem; padding: 0.5rem; }}
</style>
</head>
<body>
<h1>Visual Receipt</h1>
<p>{html.escape(payload['company'])} ({html.escape(payload['ticker'])})</p>
<div class="metric">Fair value: {payload['weighted_fair_value_per_share']:.2f}</div>
<div class="metric">Range: {payload['weighted_range_per_share'][0]:.2f} to {payload['weighted_range_per_share'][1]:.2f}</div>
<div class="metric">Label: {html.escape(payload['margin_of_safety_label'])}</div>
<h2>Boundaries</h2>
<ul>{"".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])}</ul>
</body>
</html>
"""


def assumption_walkthrough_markdown(payload: dict) -> str:
    lines = [
        "# Assumption Change Walkthrough",
        "",
        f"Company: {payload['company']} ({payload['ticker']})",
        f"Scenario: {payload['scenario']}",
        f"Changed assumption: `{payload['changed_assumption']}` {payload['prior_value']} -> {payload['new_value']}",
        "",
        "## Movement",
        "",
        f"- Weighted fair value per share: {payload['before']['weighted_fair_value_per_share']:.2f} -> {payload['after']['weighted_fair_value_per_share']:.2f} ({payload['movement']['weighted_fair_value_per_share']:+.2f})",
        f"- Weighted margin of safety: {payload['before']['weighted_margin_of_safety_pct']:.1f}% -> {payload['after']['weighted_margin_of_safety_pct']:.1f}% ({payload['movement']['weighted_margin_of_safety_pct']:+.1f} pts)",
        f"- Label: {payload['before']['margin_of_safety_label']} -> {payload['after']['margin_of_safety_label']}",
        "",
        "## Steps",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["walkthrough_steps"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def assumption_walkthrough_html(payload: dict) -> str:
    steps = "".join(f"<li>{html.escape(item)}</li>" for item in payload["walkthrough_steps"])
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Assumption Change Walkthrough</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
table {{ border-collapse: collapse; width: 100%; max-width: 760px; }}
td, th {{ border: 1px solid #ccd1d1; padding: 0.45rem; text-align: left; }}
.badge {{ display: inline-block; border: 1px solid #5d6d7e; padding: 0.2rem 0.45rem; }}
</style>
</head>
<body>
<h1>Assumption Change Walkthrough</h1>
<p>{html.escape(payload['company'])} ({html.escape(payload['ticker'])})</p>
<p class="badge">Research only; no advice or execution.</p>
<p>Scenario: {html.escape(payload['scenario'])}</p>
<p>Changed assumption: <code>{html.escape(payload['changed_assumption'])}</code> {payload['prior_value']} to {payload['new_value']}</p>
<table><thead><tr><th>Metric</th><th>Before</th><th>After</th><th>Movement</th></tr></thead><tbody>
<tr><td>Weighted fair value per share</td><td>{payload['before']['weighted_fair_value_per_share']:.2f}</td><td>{payload['after']['weighted_fair_value_per_share']:.2f}</td><td>{payload['movement']['weighted_fair_value_per_share']:+.2f}</td></tr>
<tr><td>Weighted margin of safety</td><td>{payload['before']['weighted_margin_of_safety_pct']:.1f}%</td><td>{payload['after']['weighted_margin_of_safety_pct']:.1f}%</td><td>{payload['movement']['weighted_margin_of_safety_pct']:+.1f} pts</td></tr>
<tr><td>Label</td><td>{html.escape(payload['before']['margin_of_safety_label'])}</td><td>{html.escape(payload['after']['margin_of_safety_label'])}</td><td>review context</td></tr>
</tbody></table>
<h2>Steps</h2><ul>{steps}</ul>
<h2>Boundaries</h2><ul>{boundaries}</ul>
</body>
</html>
"""


def demo_gallery_markdown(payload: dict) -> str:
    lines = [
        "# Multi-Company Demo Gallery",
        "",
        payload["gallery_note"],
        "",
        "| Company | Ticker | Fair Value | Range | MOS | Label | Scenarios |",
        "| --- | --- | ---: | --- | ---: | --- | ---: |",
    ]
    for item in payload["cards"]:
        lines.append(
            f"| {item['company']} | {item['ticker']} | {item['currency']} {item['weighted_fair_value_per_share']:.2f} | "
            f"{item['weighted_range_per_share'][0]:.2f} to {item['weighted_range_per_share'][1]:.2f} | "
            f"{item['weighted_margin_of_safety_pct']:.1f}% | {item['margin_of_safety_label']} | {item['scenario_count']} |"
        )
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def demo_gallery_html(payload: dict) -> str:
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(item['company'])}</td>"
        f"<td>{html.escape(item['ticker'])}</td>"
        f"<td>{html.escape(item['currency'])} {item['weighted_fair_value_per_share']:.2f}</td>"
        f"<td>{item['weighted_range_per_share'][0]:.2f} to {item['weighted_range_per_share'][1]:.2f}</td>"
        f"<td>{item['weighted_margin_of_safety_pct']:.1f}%</td>"
        f"<td>{html.escape(item['margin_of_safety_label'])}</td>"
        f"<td>{item['scenario_count']}</td>"
        "</tr>"
        for item in payload["cards"]
    )
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Multi-Company Demo Gallery</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ccd1d1; padding: 0.45rem; text-align: left; }}
.note {{ color: #566573; }}
</style>
</head>
<body>
<h1>Multi-Company Demo Gallery</h1>
<p class="note">{html.escape(payload['gallery_note'])}</p>
<table><thead><tr><th>Company</th><th>Ticker</th><th>Fair Value</th><th>Range</th><th>MOS</th><th>Label</th><th>Scenarios</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Boundaries</h2><ul>{boundaries}</ul>
</body>
</html>
"""


def decision_journal_markdown(payload: dict) -> str:
    lines = [
        "# Decision Journal",
        "",
        f"Company: {payload['company']} ({payload['ticker']})",
        "",
        f"Summary decision: {payload['summary_decision']}",
        "",
        "## Entries",
        "",
    ]
    for item in payload["journal_entries"]:
        lines.append(f"- {item['id']} {item['scenario']}: {item['decision']}; {item['rationale']}")
    lines.extend(["", "## Open Questions", ""])
    lines.extend(f"- {item}" for item in payload["open_questions"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def public_readiness_payload(packet: dict) -> dict:
    return {
        "schema_version": "valuation-scenario-lab.public-readiness.v0.5",
        "generated_on": "static-local",
        "headline": "Offline valuation scenario lab",
        "subhead": "Deterministic Markdown, JSON, and static HTML artifacts from local assumptions.",
        "primary_ctas": [
            {
                "label": "Run the demo",
                "command": "valuation-scenario-lab demo",
                "artifact": "demo/valuation-packet.html",
            },
            {
                "label": "Validate release",
                "command": "valuation-scenario-lab validate-release --format markdown",
                "artifact": "release/release-manifest.md",
            },
            {
                "label": "Read the journal",
                "command": "valuation-scenario-lab decision-journal --packet demo/valuation-packet.json --ledger demo/review-ledger.json --output demo",
                "artifact": "demo/decision-journal.md",
            },
            {
                "label": "Read the thesis brief",
                "command": "valuation-scenario-lab thesis-brief --root . --output demo",
                "artifact": "demo/thesis-brief.md",
            },
            {
                "label": "Read the reviewer scorecard",
                "command": "valuation-scenario-lab reviewer-scorecard --root . --output demo",
                "artifact": "demo/reviewer-scorecard.html",
            },
            {
                "label": "Open troubleshooting",
                "command": "valuation-scenario-lab troubleshoot --root . --output demo",
                "artifact": "demo/troubleshoot.html",
            },
            {
                "label": "Copy README snippet",
                "command": "valuation-scenario-lab readme-snippet --root . --output demo",
                "artifact": "demo/readme-snippet.md",
            },
            {
                "label": "Open release deck",
                "command": "valuation-scenario-lab release-deck --root . --output demo",
                "artifact": "demo/release-deck.html",
            },
            {
                "label": "Export scenario cards",
                "command": "valuation-scenario-lab scenario-library --fixtures examples --output demo",
                "artifact": "demo/scenario-library.html",
            },
            {
                "label": "Doctor fixtures",
                "command": "valuation-scenario-lab fixture-doctor --fixtures examples --policy examples/review-policy.json --format markdown",
                "artifact": "demo/fixture-doctor.md",
            },
        ],
        "demo_company": packet.get("company"),
        "demo_ticker": packet.get("ticker"),
        "demo_outputs": [
            "demo/valuation-packet.html",
            "demo/quickstart-check.md",
            "demo/visual-receipt.html",
            "demo/showcase-dashboard.svg",
            "demo/showcase-dashboard.html",
            "demo/thesis-brief.html",
            "demo/scenario-library.html",
            "demo/reviewer-scorecard.html",
            "demo/troubleshoot.html",
            "demo/readme-snippet.html",
            "demo/release-deck.html",
            "demo/decision-journal.md",
            "demo/assumption-change-walkthrough.html",
            "demo/multi-company-demo-gallery.html",
            "demo/fixture-doctor.md",
            "demo/public-readiness-landing.html",
        ],
        "readiness_checks": [
            "zero runtime dependencies",
            "static local fixtures",
            "deterministic demo artifacts",
            "fixture doctor schema, weight, numeric, and staleness checks",
            "public-neutral boundary text",
            "no workflow automation",
        ],
        "boundaries": packet.get("boundaries", []),
    }


def public_readiness_markdown(payload: dict) -> str:
    lines = ["# Public Readiness Landing", "", payload["headline"], "", payload["subhead"], "", "## CTAs", ""]
    lines.extend(f"- {item['label']}: `{item['command']}` -> `{item['artifact']}`" for item in payload["primary_ctas"])
    lines.extend(["", "## Demo Outputs", ""])
    lines.extend(f"- `{item}`" for item in payload["demo_outputs"])
    lines.extend(["", "## Readiness Checks", ""])
    lines.extend(f"- {item}" for item in payload["readiness_checks"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def public_readiness_html(payload: dict) -> str:
    ctas = "".join(
        "<li>"
        f"<strong>{html.escape(item['label'])}</strong>"
        f"<code>{html.escape(item['command'])}</code>"
        f"<span>{html.escape(item['artifact'])}</span>"
        "</li>"
        for item in payload["primary_ctas"]
    )
    checks = "".join(f"<li>{html.escape(item)}</li>" for item in payload["readiness_checks"])
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    outputs = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in payload["demo_outputs"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Valuation Scenario Lab Public Readiness</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 0; color: #17202a; background: #f7f9fb; }}
main {{ max-width: 960px; margin: 0 auto; padding: 3rem 1.25rem; }}
header {{ border-bottom: 2px solid #566573; padding-bottom: 1.5rem; }}
h1 {{ font-size: 2.4rem; margin: 0 0 0.5rem; }}
section {{ margin-top: 2rem; }}
ul {{ padding-left: 1.25rem; }}
.cta-list li {{ margin: 0.75rem 0; }}
code {{ display: inline-block; margin: 0 0.5rem; padding: 0.15rem 0.35rem; background: #eaf0f6; }}
</style>
</head>
<body>
<main>
<header>
<h1>{html.escape(payload['headline'])}</h1>
<p>{html.escape(payload['subhead'])}</p>
<p>Demo fixture: {html.escape(payload['demo_company'])} ({html.escape(payload['demo_ticker'])})</p>
</header>
<section><h2>First Actions</h2><ul class="cta-list">{ctas}</ul></section>
<section><h2>Demo Outputs</h2><ul>{outputs}</ul></section>
<section><h2>Readiness Checks</h2><ul>{checks}</ul></section>
<section><h2>Boundaries</h2><ul>{boundaries}</ul></section>
</main>
</body>
</html>
"""


def showcase_payload(packet: dict[str, Any], gallery: dict[str, Any], doctor: dict[str, Any], matrix: dict[str, Any]) -> dict[str, Any]:
    matrix_rows = matrix.get("rows", [])
    lowest = min(matrix_rows, key=lambda item: float(item["weighted_fair_value_per_share"]))
    highest = max(matrix_rows, key=lambda item: float(item["weighted_fair_value_per_share"]))
    return {
        "schema_version": "valuation-scenario-lab.showcase-dashboard.v0.6",
        "generated_on": "static-local",
        "title": "Valuation Scenario Lab Showcase Dashboard",
        "company": packet["company"],
        "ticker": packet["ticker"],
        "weighted_fair_value_per_share": packet["weighted_fair_value_per_share"],
        "weighted_range_per_share": packet["weighted_range_per_share"],
        "weighted_margin_of_safety_pct": packet["weighted_margin_of_safety_pct"],
        "margin_of_safety_label": packet["margin_of_safety_label"],
        "scenario_count": len(packet.get("valuation_ranges", [])),
        "gallery_company_count": gallery["company_count"],
        "gallery_tickers": [item["ticker"] for item in gallery.get("cards", [])],
        "fixture_doctor_status": doctor["status"],
        "fixture_issue_count": doctor["issue_count"],
        "sensitivity_case_count": len(matrix_rows),
        "sensitivity_low_fair_value": lowest["weighted_fair_value_per_share"],
        "sensitivity_high_fair_value": highest["weighted_fair_value_per_share"],
        "source_artifacts": [
            "demo/valuation-packet.json",
            "demo/multi-company-demo-gallery.json",
            "demo/fixture-doctor.json",
            "demo/sensitivity-matrix.json",
        ],
        "boundaries": packet.get("boundaries", []),
    }


def showcase_markdown(payload: dict[str, Any]) -> str:
    return f"""# {payload['title']}

Company: {payload['company']} ({payload['ticker']})

Weighted fair value per share: {payload['weighted_fair_value_per_share']:.2f}
Weighted range per share: {payload['weighted_range_per_share'][0]:.2f} to {payload['weighted_range_per_share'][1]:.2f}
Margin-of-safety label: {payload['margin_of_safety_label']} ({payload['weighted_margin_of_safety_pct']:.1f}%)

## Showcase Inputs

- Demo packet scenarios: {payload['scenario_count']}
- Gallery companies: {payload['gallery_company_count']} ({", ".join(payload['gallery_tickers'])})
- Fixture doctor: {payload['fixture_doctor_status']} with {payload['fixture_issue_count']} issues
- Sensitivity cases: {payload['sensitivity_case_count']} from {payload['sensitivity_low_fair_value']:.2f} to {payload['sensitivity_high_fair_value']:.2f}

## Shareable Visual

Open `demo/showcase-dashboard.svg` or `demo/showcase-dashboard.html`.

## Boundaries

{chr(10).join(f"- {item}" for item in payload["boundaries"])}
"""


def showcase_html(payload: dict[str, Any]) -> str:
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    sources = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in payload["source_artifacts"])
    svg = showcase_svg(payload)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(payload['title'])}</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 0; color: #17202a; background: #f6f8fa; }}
main {{ max-width: 1040px; margin: 0 auto; padding: 2rem 1rem; }}
.visual {{ overflow-x: auto; background: #ffffff; border: 1px solid #d6dde4; padding: 1rem; }}
svg {{ max-width: 100%; height: auto; display: block; }}
code {{ background: #eef3f8; padding: 0.1rem 0.25rem; }}
</style>
</head>
<body>
<main>
<h1>{html.escape(payload['title'])}</h1>
<p>{html.escape(payload['company'])} ({html.escape(payload['ticker'])}) static showcase from local demo artifacts.</p>
<div class="visual">{svg}</div>
<h2>Source Artifacts</h2>
<ul>{sources}</ul>
<h2>Boundaries</h2>
<ul>{boundaries}</ul>
</main>
</body>
</html>
"""


def showcase_svg(payload: dict[str, Any]) -> str:
    title = html.escape(payload["title"])
    company = html.escape(payload["company"])
    ticker = html.escape(payload["ticker"])
    label = html.escape(payload["margin_of_safety_label"])
    doctor = html.escape(payload["fixture_doctor_status"])
    tickers = html.escape(", ".join(payload["gallery_tickers"]))
    boundaries = [html.escape(item) for item in payload["boundaries"]]
    mos = float(payload["weighted_margin_of_safety_pct"])
    mos_width = max(0, min(240, int(round((mos + 40.0) / 80.0 * 240.0))))
    low = float(payload["sensitivity_low_fair_value"])
    high = float(payload["sensitivity_high_fair_value"])
    fair = float(payload["weighted_fair_value_per_share"])
    sensitivity_width = max(10, min(240, int(round((fair - low) / max(high - low, 0.01) * 240.0))))
    boundary_text = "".join(f'<text x="72" y="{552 + index * 22}" class="small">- {item}</text>' for index, item in enumerate(boundaries))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="700" viewBox="0 0 960 700" role="img" aria-labelledby="title desc">
<title id="title">{title}</title>
<desc id="desc">Static no-dependency dashboard summarizing the current demo packet, gallery, fixture doctor, and sensitivity matrix.</desc>
<style>
.bg {{ fill: #f6f8fa; }}
.panel {{ fill: #ffffff; stroke: #ccd6df; stroke-width: 1.5; }}
.ink {{ fill: #17202a; font-family: Arial, sans-serif; }}
.muted {{ fill: #5d6d7e; font-family: Arial, sans-serif; }}
.small {{ fill: #34495e; font-family: Arial, sans-serif; font-size: 15px; }}
.label {{ fill: #5d6d7e; font-family: Arial, sans-serif; font-size: 13px; text-transform: uppercase; }}
.metric {{ fill: #17202a; font-family: Arial, sans-serif; font-size: 30px; font-weight: 700; }}
.accent {{ fill: #2e7d6b; }}
.warn {{ fill: #b65d22; }}
.bar-bg {{ fill: #e8edf2; }}
</style>
<rect class="bg" width="960" height="660"/>
<text x="48" y="58" class="ink" font-size="32" font-weight="700">{title}</text>
<text x="48" y="88" class="muted" font-size="17">{company} ({ticker}) - generated_on static-local</text>
<rect x="48" y="124" width="264" height="150" rx="6" class="panel"/>
<text x="72" y="160" class="label">Weighted fair value</text>
<text x="72" y="204" class="metric">{fair:.2f}</text>
<text x="72" y="238" class="small">Range {payload['weighted_range_per_share'][0]:.2f} to {payload['weighted_range_per_share'][1]:.2f}</text>
<rect x="348" y="124" width="264" height="150" rx="6" class="panel"/>
<text x="372" y="160" class="label">Margin of safety</text>
<text x="372" y="204" class="metric">{mos:.1f}%</text>
<rect x="372" y="224" width="240" height="14" class="bar-bg"/>
<rect x="372" y="224" width="{mos_width}" height="14" class="warn"/>
<text x="372" y="258" class="small">{label}</text>
<rect x="648" y="124" width="264" height="150" rx="6" class="panel"/>
<text x="672" y="160" class="label">Fixture doctor</text>
<text x="672" y="204" class="metric">{doctor}</text>
<text x="672" y="238" class="small">{payload['fixture_issue_count']} issues across bundled fixtures</text>
<rect x="48" y="306" width="414" height="178" rx="6" class="panel"/>
<text x="72" y="342" class="label">Gallery</text>
<text x="72" y="386" class="metric">{payload['gallery_company_count']} companies</text>
<text x="72" y="422" class="small">{tickers}</text>
<text x="72" y="456" class="small">{payload['scenario_count']} packet scenarios in the primary demo</text>
<rect x="498" y="306" width="414" height="178" rx="6" class="panel"/>
<text x="522" y="342" class="label">Sensitivity matrix</text>
<text x="522" y="386" class="metric">{payload['sensitivity_case_count']} cases</text>
<rect x="522" y="410" width="240" height="16" class="bar-bg"/>
<rect x="522" y="410" width="{sensitivity_width}" height="16" class="accent"/>
<text x="522" y="456" class="small">Fair value span {low:.2f} to {high:.2f}</text>
<text x="48" y="526" class="label">Finance boundaries</text>
{boundary_text}
</svg>
"""


def thesis_brief_markdown(payload: dict[str, Any]) -> str:
    snapshot = payload["packet_snapshot"]
    lines = [
        "# Thesis Brief",
        "",
        f"Company: {payload['company']} ({payload['ticker']})",
        "",
        payload["thesis_summary"],
        "",
        "## Packet Snapshot",
        "",
        f"- Current price: {payload['currency']} {snapshot['current_price']:.2f}",
        f"- Weighted fair value per share: {payload['currency']} {snapshot['weighted_fair_value_per_share']:.2f}",
        f"- Weighted range per share: {payload['currency']} {snapshot['weighted_range_per_share'][0]:.2f} to {payload['currency']} {snapshot['weighted_range_per_share'][1]:.2f}",
        f"- Margin-of-safety label: {snapshot['margin_of_safety_label']} ({snapshot['weighted_margin_of_safety_pct']:.1f}%)",
        "",
        "## Scenario Thesis",
        "",
        "| Scenario | Weight | Base | Range | Label |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for item in payload["scenario_thesis"]:
        lines.append(
            f"| {item['scenario']} | {item['weight']:.3f} | {item['base']:.2f} | "
            f"{item['range'][0]:.2f} to {item['range'][1]:.2f} | {item['margin_label']} |"
        )
    lines.extend(["", "## History Changes", ""])
    lines.extend(f"- {item['field']}: {item['prior']} -> {item['current']}" for item in payload["history_changes"])
    lines.extend(["", "## Open Questions", ""])
    lines.extend(f"- {item}" for item in payload["open_questions"])
    lines.extend(["", "## Evidence Artifacts", ""])
    lines.extend(f"- `{item}`" for item in payload["evidence_artifacts"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def thesis_brief_html(payload: dict[str, Any]) -> str:
    snapshot = payload["packet_snapshot"]
    scenarios = "".join(
        "<tr>"
        f"<td>{html.escape(item['scenario'])}</td>"
        f"<td>{item['weight']:.3f}</td>"
        f"<td>{item['base']:.2f}</td>"
        f"<td>{item['range'][0]:.2f} to {item['range'][1]:.2f}</td>"
        f"<td>{html.escape(item['margin_label'])}</td>"
        "</tr>"
        for item in payload["scenario_thesis"]
    )
    changes = "".join(
        f"<li>{html.escape(item['field'])}: {html.escape(str(item['prior']))} to {html.escape(str(item['current']))}</li>"
        for item in payload["history_changes"]
    )
    questions = "".join(f"<li>{html.escape(item)}</li>" for item in payload["open_questions"])
    evidence = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in payload["evidence_artifacts"])
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Thesis Brief</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ccd1d1; padding: 0.45rem; text-align: left; }}
.metric {{ border: 1px solid #ccd1d1; display: inline-block; margin: 0.25rem; padding: 0.5rem; }}
code {{ background: #eef3f8; padding: 0.1rem 0.25rem; }}
</style>
</head>
<body>
<h1>Thesis Brief</h1>
<p>{html.escape(payload['company'])} ({html.escape(payload['ticker'])})</p>
<p>{html.escape(payload['thesis_summary'])}</p>
<div class="metric">Fair value: {html.escape(payload['currency'])} {snapshot['weighted_fair_value_per_share']:.2f}</div>
<div class="metric">Range: {snapshot['weighted_range_per_share'][0]:.2f} to {snapshot['weighted_range_per_share'][1]:.2f}</div>
<div class="metric">Label: {html.escape(snapshot['margin_of_safety_label'])}</div>
<h2>Scenario Thesis</h2>
<table><thead><tr><th>Scenario</th><th>Weight</th><th>Base</th><th>Range</th><th>Label</th></tr></thead><tbody>{scenarios}</tbody></table>
<h2>History Changes</h2><ul>{changes}</ul>
<h2>Open Questions</h2><ul>{questions}</ul>
<h2>Evidence Artifacts</h2><ul>{evidence}</ul>
<h2>Boundaries</h2><ul>{boundaries}</ul>
</body>
</html>
"""


def scenario_library_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Scenario Library",
        "",
        f"Companies: {payload['company_count']}",
        f"Cards: {payload['card_count']}",
        "",
        "| ID | Company | Scenario | Growth | FCF Margin | Discount | Base | Label |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in payload["cards"]:
        assumptions = item["assumptions"]
        outputs = item["model_outputs"]
        lines.append(
            f"| {item['id']} | {item['company']} | {item['scenario']} | "
            f"{assumptions['revenue_growth_pct']:.1f}% | {assumptions['fcf_margin_pct']:.1f}% | "
            f"{assumptions['discount_rate_pct']:.1f}% | {outputs['base_value_per_share']:.2f} | {outputs['margin_label']} |"
        )
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def scenario_library_html(payload: dict[str, Any]) -> str:
    rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(item['id'])}</code></td>"
        f"<td>{html.escape(item['company'])}</td>"
        f"<td>{html.escape(item['scenario'])}</td>"
        f"<td>{item['assumptions']['revenue_growth_pct']:.1f}%</td>"
        f"<td>{item['assumptions']['fcf_margin_pct']:.1f}%</td>"
        f"<td>{item['assumptions']['discount_rate_pct']:.1f}%</td>"
        f"<td>{item['model_outputs']['base_value_per_share']:.2f}</td>"
        f"<td>{html.escape(item['model_outputs']['margin_label'])}</td>"
        "</tr>"
        for item in payload["cards"]
    )
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Scenario Library</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ccd1d1; padding: 0.45rem; text-align: left; }}
code {{ background: #eef3f8; padding: 0.1rem 0.25rem; }}
</style>
</head>
<body>
<h1>Scenario Library</h1>
<p>{payload['card_count']} reusable assumption cards from bundled fictional fixtures.</p>
<table><thead><tr><th>ID</th><th>Company</th><th>Scenario</th><th>Growth</th><th>FCF Margin</th><th>Discount</th><th>Base</th><th>Label</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Boundaries</h2><ul>{boundaries}</ul>
</body>
</html>
"""


def relative_output(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def sample_workflow_payload(root: Path) -> dict[str, Any]:
    steps = [
        {
            "step": 1,
            "name": "Generate the full demo tree",
            "command": "valuation-scenario-lab demo --root .",
            "artifacts": ["demo/valuation-packet.json", "demo/valuation-packet.md", "demo/valuation-packet.html"],
        },
        {
            "step": 2,
            "name": "Compare against prior assumptions",
            "command": "valuation-scenario-lab compare-history --current demo/valuation-packet.json --prior examples/prior-packet.json --output demo",
            "artifacts": ["demo/compare-history.json", "demo/compare-history.md"],
        },
        {
            "step": 3,
            "name": "Create review evidence",
            "command": "valuation-scenario-lab review-ledger --packet demo/valuation-packet.json --policy examples/review-policy.json --output demo",
            "artifacts": ["demo/review-ledger.json", "demo/review-ledger.md"],
        },
        {
            "step": 4,
            "name": "Stress local assumptions",
            "command": "valuation-scenario-lab sensitivity-matrix --fixtures examples --output demo",
            "artifacts": ["demo/sensitivity-matrix.json", "demo/sensitivity-matrix.md"],
        },
        {
            "step": 5,
            "name": "Explain one assumption change",
            "command": "valuation-scenario-lab assumption-change-walkthrough --fixtures examples --output demo",
            "artifacts": [
                "demo/assumption-change-walkthrough.json",
                "demo/assumption-change-walkthrough.md",
                "demo/assumption-change-walkthrough.html",
            ],
        },
        {
            "step": 6,
            "name": "Review fixture quality",
            "command": "valuation-scenario-lab fixture-doctor --fixtures examples --policy examples/review-policy.json --format markdown --output demo",
            "artifacts": ["demo/fixture-doctor.json", "demo/fixture-doctor.md"],
        },
        {
            "step": 7,
            "name": "Summarize analyst outputs",
            "command": "valuation-scenario-lab thesis-brief --root . --output demo",
            "artifacts": ["demo/thesis-brief.json", "demo/thesis-brief.md", "demo/thesis-brief.html"],
        },
        {
            "step": 8,
            "name": "Publish static demo views",
            "command": "valuation-scenario-lab public-readiness-landing --root . --output demo",
            "artifacts": [
                "demo/public-readiness-landing.json",
                "demo/public-readiness-landing.md",
                "demo/public-readiness-landing.html",
                "demo/showcase-dashboard.svg",
                "demo/showcase-dashboard.html",
                "demo/scenario-library.html",
            ],
        },
        {
            "step": 9,
            "name": "Record release reproducibility",
            "command": "valuation-scenario-lab reproducibility-audit --root . --output demo",
            "artifacts": [
                "demo/reproducibility-audit.json",
                "demo/reproducibility-audit.md",
                "demo/reproducibility-audit.html",
                "release/release-manifest.json",
                "release/release-manifest.md",
            ],
        },
        {
            "step": 10,
            "name": "Score reviewer operability",
            "command": "valuation-scenario-lab reviewer-scorecard --root . --output demo",
            "artifacts": [
                "demo/reviewer-scorecard.json",
                "demo/reviewer-scorecard.md",
                "demo/reviewer-scorecard.html",
            ],
        },
        {
            "step": 11,
            "name": "Map common diagnostics",
            "command": "valuation-scenario-lab troubleshoot --root . --output demo",
            "artifacts": [
                "demo/troubleshoot.json",
                "demo/troubleshoot.md",
                "demo/troubleshoot.html",
            ],
        },
        {
            "step": 12,
            "name": "Prepare public promotion snippets",
            "command": "valuation-scenario-lab readme-snippet --root . --output demo && valuation-scenario-lab release-deck --root . --output demo",
            "artifacts": [
                "demo/readme-snippet.json",
                "demo/readme-snippet.md",
                "demo/readme-snippet.html",
                "demo/release-deck.json",
                "demo/release-deck.md",
                "demo/release-deck.html",
            ],
        },
        {
            "step": 13,
            "name": "Document install and bundle stability",
            "command": "valuation-scenario-lab install-smoke-receipt --root . --output release && valuation-scenario-lab export-bundle --root . --output release",
            "artifacts": [
                "release/install-smoke-receipt.json",
                "release/install-smoke-receipt.md",
                "release/install-smoke-receipt.html",
                "release/public-bundle.json",
                "release/public-bundle.md",
                "release/public-bundle.html",
            ],
        },
    ]
    for step in steps:
        step["artifact_status"] = [{"path": item, "exists": (root / item).exists()} for item in step["artifacts"]]
    required_artifacts = [
        item
        for step in steps
        for item in step["artifact_status"]
        if not item["path"].startswith(("demo/reproducibility-audit", "demo/reviewer-scorecard", "demo/troubleshoot", "demo/readme-snippet", "demo/release-deck"))
    ]
    return {
        "schema_version": "valuation-scenario-lab.sample-workflow.v0.8",
        "status": "pass" if all(item["exists"] for item in required_artifacts) else "fail",
        "generated_on": "static-local",
        "title": "Sample Analyst Workflow Receipt",
        "steps": steps,
        "primary_commands": [step["command"] for step in steps],
        "boundaries": [
            "No live data.",
            "No broker connections.",
            "No buy/sell/hold advice.",
        ],
    }


def sample_workflow_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Sample Analyst Workflow Receipt", "", f"Status: {payload['status']}", "", "## Steps", ""]
    for step in payload["steps"]:
        lines.append(f"### {step['step']}. {step['name']}")
        lines.append("")
        lines.append(f"Command: `{step['command']}`")
        lines.append("")
        lines.extend(f"- `{item['path']}`: {'ok' if item['exists'] else 'missing'}" for item in step["artifact_status"])
        lines.append("")
    lines.extend(["## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def sample_workflow_html(payload: dict[str, Any]) -> str:
    steps = []
    for step in payload["steps"]:
        artifacts = "".join(
            f"<li><code>{html.escape(item['path'])}</code>: {'ok' if item['exists'] else 'missing'}</li>"
            for item in step["artifact_status"]
        )
        steps.append(
            "<section>"
            f"<h2>{step['step']}. {html.escape(step['name'])}</h2>"
            f"<p><code>{html.escape(step['command'])}</code></p>"
            f"<ul>{artifacts}</ul>"
            "</section>"
        )
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Sample Analyst Workflow Receipt</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
section {{ border-top: 1px solid #d6dde4; padding: 1rem 0; }}
code {{ background: #eef3f8; padding: 0.1rem 0.25rem; }}
</style>
</head>
<body>
<h1>Sample Analyst Workflow Receipt</h1>
<p>Status: {html.escape(payload['status'])}</p>
{''.join(steps)}
<h2>Boundaries</h2><ul>{boundaries}</ul>
</body>
</html>
"""


def casebook_payload(packet: dict[str, Any], library: dict[str, Any], thesis: dict[str, Any], workflow: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "valuation-scenario-lab.casebook.v0.9",
        "generated_on": "static-local",
        "title": "Public Valuation Scenario Casebook",
        "audience": "stranger-readable public walkthrough of deterministic local artifacts",
        "company": packet["company"],
        "ticker": packet["ticker"],
        "walkthrough": [
            {
                "section": "Packet",
                "artifact": "demo/valuation-packet.html",
                "summary": f"{packet['company']} has a weighted fair value of {packet['currency']} {packet['weighted_fair_value_per_share']:.2f} across {len(packet['valuation_ranges'])} local scenarios.",
            },
            {
                "section": "Scenario Library",
                "artifact": "demo/scenario-library.html",
                "summary": f"{library['card_count']} reusable scenario cards across {library['company_count']} fictional companies document the assumption set.",
            },
            {
                "section": "Thesis Brief",
                "artifact": "demo/thesis-brief.html",
                "summary": thesis["thesis_summary"],
            },
            {
                "section": "Workflow Receipt",
                "artifact": "demo/sample-workflow.html",
                "summary": f"{len(workflow['steps'])} command steps connect source fixtures to public artifacts.",
            },
            {
                "section": "Reproducibility Audit",
                "artifact": "demo/reproducibility-audit.html",
                "summary": f"Audit status is {audit['status']} for artifact, schema, dependency, manifest, and boundary checks.",
            },
        ],
        "source_artifacts": [
            "demo/valuation-packet.json",
            "demo/scenario-library.json",
            "demo/thesis-brief.json",
            "demo/sample-workflow.json",
            "demo/reproducibility-audit.json",
        ],
        "reader_prompts": [
            "Which assumption would you inspect first, and which artifact records it?",
            "Which boundary prevents this walkthrough from becoming a recommendation?",
            "Can another reviewer regenerate the same artifact set from local files?",
        ],
        "boundaries": [
            "No live data.",
            "No broker connections.",
            "No buy/sell/hold advice.",
        ],
    }


def casebook_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# {payload['title']}",
        "",
        f"Company: {payload['company']} ({payload['ticker']})",
        "",
        payload["audience"],
        "",
        "## Walkthrough",
        "",
    ]
    for index, item in enumerate(payload["walkthrough"], start=1):
        lines.append(f"### {index}. {item['section']}")
        lines.append("")
        lines.append(f"Artifact: `{item['artifact']}`")
        lines.append("")
        lines.append(item["summary"])
        lines.append("")
    lines.extend(["## Source Artifacts", ""])
    lines.extend(f"- `{item}`" for item in payload["source_artifacts"])
    lines.extend(["", "## Reader Prompts", ""])
    lines.extend(f"- {item}" for item in payload["reader_prompts"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def casebook_html(payload: dict[str, Any]) -> str:
    walkthrough = "".join(
        "<section>"
        f"<h2>{index}. {html.escape(item['section'])}</h2>"
        f"<p><code>{html.escape(item['artifact'])}</code></p>"
        f"<p>{html.escape(item['summary'])}</p>"
        "</section>"
        for index, item in enumerate(payload["walkthrough"], start=1)
    )
    sources = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in payload["source_artifacts"])
    prompts = "".join(f"<li>{html.escape(item)}</li>" for item in payload["reader_prompts"])
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(payload['title'])}</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
section {{ border-top: 1px solid #d6dde4; padding: 1rem 0; }}
code {{ background: #eef3f8; padding: 0.1rem 0.25rem; }}
.note {{ color: #566573; }}
</style>
</head>
<body>
<h1>{html.escape(payload['title'])}</h1>
<p>{html.escape(payload['company'])} ({html.escape(payload['ticker'])})</p>
<p class="note">{html.escape(payload['audience'])}</p>
{walkthrough}
<h2>Source Artifacts</h2><ul>{sources}</ul>
<h2>Reader Prompts</h2><ul>{prompts}</ul>
<h2>Boundaries</h2><ul>{boundaries}</ul>
</body>
</html>
"""


def reviewer_scorecard_payload(root: Path, output: Path) -> dict[str, Any]:
    validation = validate_release_payload(root)
    validation_status = validation_status_ignoring_generated_operability(validation)
    schemas = schema_version_checks(root)
    schema_status = schema_status_ignoring_generated_operability(schemas)
    boundaries = safety_boundary_checks(root)
    doctor_path = output / "fixture-doctor.json"
    doctor = read_json(doctor_path) if doctor_path.exists() else {"status": "missing", "issue_count": 99}
    criteria = {
        "product": [
            criterion("Complete demo narrative", 7, all((output / name).exists() for name in [
                "valuation-packet.html",
                "thesis-brief.html",
                "casebook.html",
                "public-readiness-landing.html",
            ]), ["demo/valuation-packet.html", "demo/thesis-brief.html", "demo/casebook.html", "demo/public-readiness-landing.html"]),
            criterion("Review evidence chain", 6, all((output / name).exists() for name in [
                "review-ledger.json",
                "decision-journal.json",
                "sample-workflow.json",
            ]), ["demo/review-ledger.json", "demo/decision-journal.json", "demo/sample-workflow.json"]),
            criterion("Scenario explainability", 6, all((output / name).exists() for name in [
                "scenario-library.json",
                "sensitivity-matrix.json",
                "assumption-change-walkthrough.json",
            ]), ["demo/scenario-library.json", "demo/sensitivity-matrix.json", "demo/assumption-change-walkthrough.json"]),
            criterion("Packaged public docs", 6, all((root / name).exists() for name in [
                "README.md",
                "docs/release-checks.md",
                "RELEASE_NOTES.md",
            ]), ["README.md", "docs/release-checks.md", "RELEASE_NOTES.md"]),
        ],
        "engineering": [
            criterion("Release validation passes", 8, validation_status == "pass", ["valuation-scenario-lab validate-release --root ."]),
            criterion("Schema versions match", 6, schema_status == "pass", ["demo/*.json", "release/*.json"]),
            criterion("Zero runtime dependencies", 5, "dependencies = []" in (root / "pyproject.toml").read_text(encoding="utf-8"), ["pyproject.toml"]),
            criterion("Release manifests present", 6, all((root / name).exists() for name in [
                "release/release-manifest.json",
                "release/public-bundle.json",
                "release/install-smoke-receipt.json",
            ]), ["release/release-manifest.json", "release/public-bundle.json", "release/install-smoke-receipt.json"]),
        ],
        "cold-user": [
            criterion("Quickstart or workflow receipt exists", 6, (output / "quickstart-check.json").exists() or (output / "sample-workflow.json").exists(), ["demo/quickstart-check.json", "demo/sample-workflow.json"]),
            criterion("Standalone HTML/SVG views exist", 7, all((output / name).exists() for name in [
                "showcase-dashboard.html",
                "showcase-dashboard.svg",
                "visual-receipt.html",
            ]), ["demo/showcase-dashboard.html", "demo/showcase-dashboard.svg", "demo/visual-receipt.html"]),
            criterion("Onboarding fixture scaffold exists", 6, all((output / "onboarding-template" / name).exists() for name in [
                "README.md",
                "company.json",
                "review-policy.json",
                "prior-packet.json",
            ]), ["demo/onboarding-template"]),
            criterion("Troubleshooting command documented", 6, "troubleshoot" in (root / "README.md").read_text(encoding="utf-8"), ["README.md", "valuation-scenario-lab troubleshoot --root . --output demo"]),
        ],
        "risk": [
            criterion("Safety boundaries present", 8, boundaries["status"] == "pass", ["README.md", "demo/*.md", "demo/*.html", "release/*.md", "release/*.html"]),
            criterion("Fixture doctor passes", 6, doctor.get("status") == "pass", ["demo/fixture-doctor.json"]),
            criterion("No live-data/broker path", 6, all(phrase in (root / "README.md").read_text(encoding="utf-8") for phrase in [
                "No live data.",
                "No broker connections.",
                "No buy/sell/hold advice.",
            ]), ["README.md"]),
            criterion("No workflow automation", 5, not (root / ".github" / "workflows").exists(), [".github/workflows"]),
        ],
    }
    lenses = []
    for lens, items in criteria.items():
        score = sum(item["points_awarded"] for item in items)
        lenses.append({"lens": lens, "score": score, "max_score": 25, "criteria": items})
    total = sum(item["score"] for item in lenses)
    return {
        "schema_version": "valuation-scenario-lab.reviewer-scorecard.v1.1",
        "generated_on": "static-local",
        "status": "strong" if total >= 90 else "reviewable" if total >= 75 else "needs work",
        "score": total,
        "max_score": 100,
        "rubric": "Deterministic 100-point local-artifact rubric; no live data, broker connection, ranking, or advice.",
        "lenses": lenses,
        "release_validation_status": validation_status,
        "schema_check_status": schema_status,
        "boundary_check_status": boundaries["status"],
        "boundaries": [
            "No live data.",
            "No broker connections.",
            "No buy/sell/hold advice.",
        ],
    }


def criterion(name: str, points: int, ok: bool, artifacts: list[str]) -> dict[str, Any]:
    return {
        "name": name,
        "max_points": points,
        "points_awarded": points if ok else 0,
        "status": "pass" if ok else "fail",
        "artifacts": artifacts,
    }


def validation_status_ignoring_generated_operability(validation: dict[str, Any]) -> str:
    generated = (
        "demo/reviewer-scorecard.json",
        "demo/reviewer-scorecard.md",
        "demo/reviewer-scorecard.html",
        "demo/troubleshoot.json",
        "demo/troubleshoot.md",
        "demo/troubleshoot.html",
        "demo/readme-snippet.json",
        "demo/readme-snippet.md",
        "demo/readme-snippet.html",
        "demo/release-deck.json",
        "demo/release-deck.md",
        "demo/release-deck.html",
    )
    blocking = []
    for item in validation.get("findings", []):
        if item.get("severity") != "error":
            continue
        message = str(item.get("message", ""))
        if message.startswith("missing ") and any(name in message for name in generated):
            continue
        if message.startswith("release manifest "):
            continue
        blocking.append(item)
    return "pass" if not blocking else "fail"


def schema_status_ignoring_generated_operability(schemas: dict[str, Any]) -> str:
    generated = {
        "demo/reviewer-scorecard.json",
        "demo/troubleshoot.json",
        "demo/readme-snippet.json",
        "demo/release-deck.json",
    }
    mismatches = [name for name in schemas.get("mismatches", []) if name not in generated]
    return "pass" if not mismatches else "fail"


def reviewer_scorecard_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Reviewer Scorecard",
        "",
        f"Status: {payload['status']}",
        f"Score: {payload['score']} / {payload['max_score']}",
        "",
        payload["rubric"],
        "",
    ]
    for lens in payload["lenses"]:
        lines.extend([f"## {lens['lens'].title()}", "", f"Score: {lens['score']} / {lens['max_score']}", ""])
        for item in lens["criteria"]:
            artifacts = ", ".join(f"`{artifact}`" for artifact in item["artifacts"])
            lines.append(f"- {item['status']}: {item['name']} ({item['points_awarded']}/{item['max_points']}) via {artifacts}")
        lines.append("")
    lines.extend(["## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def reviewer_scorecard_html(payload: dict[str, Any]) -> str:
    sections = []
    for lens in payload["lenses"]:
        rows = "".join(
            "<tr>"
            f"<td>{html.escape(item['name'])}</td>"
            f"<td>{html.escape(item['status'])}</td>"
            f"<td>{item['points_awarded']} / {item['max_points']}</td>"
            f"<td>{html.escape(', '.join(item['artifacts']))}</td>"
            "</tr>"
            for item in lens["criteria"]
        )
        sections.append(
            f"<section><h2>{html.escape(lens['lens'].title())}</h2>"
            f"<p>Score: {lens['score']} / {lens['max_score']}</p>"
            f"<table><thead><tr><th>Criterion</th><th>Status</th><th>Points</th><th>Artifacts</th></tr></thead><tbody>{rows}</tbody></table></section>"
        )
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Reviewer Scorecard</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
section {{ border-top: 1px solid #d6dde4; padding: 1rem 0; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ccd1d1; padding: 0.45rem; text-align: left; vertical-align: top; }}
.score {{ font-size: 1.4rem; font-weight: 700; }}
</style>
</head>
<body>
<h1>Reviewer Scorecard</h1>
<p class="score">{payload['score']} / {payload['max_score']} - {html.escape(payload['status'])}</p>
<p>{html.escape(payload['rubric'])}</p>
{''.join(sections)}
<h2>Boundaries</h2><ul>{boundaries}</ul>
</body>
</html>
"""


def troubleshoot_payload(root: Path) -> dict[str, Any]:
    validation = validate_release_payload(root)
    validation_status = validation_status_ignoring_generated_operability(validation)
    problems = [
        trouble(
            "missing-demo-artifact",
            "A demo file is missing after checkout or regeneration.",
            "Run the full deterministic demo and then quickstart validation.",
            ["valuation-scenario-lab demo --root .", "valuation-scenario-lab quickstart-check --root . --output demo"],
            ["demo/quickstart-check.json", "demo/reproducibility-audit.json"],
        ),
        trouble(
            "fixture-doctor-fails",
            "Fixture schema, weights, numeric fields, or source freshness need review.",
            "Run fixture diagnostics and inspect issue paths before rebuilding packets.",
            ["valuation-scenario-lab fixture-doctor --fixtures examples --policy examples/review-policy.json --format markdown"],
            ["examples/company.json", "examples/review-policy.json", "demo/fixture-doctor.md"],
        ),
        trouble(
            "release-validation-fails",
            "Release validation reports missing files, private terms, metadata issues, or boundary gaps.",
            "Generate release receipts, refresh manifests, and rerun validation.",
            ["valuation-scenario-lab install-smoke-receipt --root . --output release", "valuation-scenario-lab export-bundle --root . --output release", "valuation-scenario-lab release-manifest --root . --output release", "valuation-scenario-lab validate-release --root . --format markdown"],
            ["release/install-smoke-receipt.json", "release/public-bundle.json", "release/release-manifest.json"],
        ),
        trouble(
            "schema-mismatch",
            "A generated JSON artifact carries an unexpected schema version.",
            "Regenerate demo and release artifacts with the current package version.",
            ["valuation-scenario-lab demo --root .", "valuation-scenario-lab reproducibility-audit --root . --output demo"],
            ["demo/reproducibility-audit.json", "src/valuation_scenario_lab/release.py"],
        ),
        trouble(
            "scorecard-below-90",
            "Reviewer scorecard is below the strong threshold.",
            "Open each failed criterion and regenerate the command named in its artifacts list.",
            ["valuation-scenario-lab reviewer-scorecard --root . --output demo", "valuation-scenario-lab troubleshoot --root . --output demo"],
            ["demo/reviewer-scorecard.json", "demo/troubleshoot.md"],
        ),
        trouble(
            "empty-directory-wheel-smoke",
            "A wheel-installed user runs commands outside the repository.",
            "Use selfcheck, which falls back to packaged data roots, or pass an explicit unpacked root.",
            ["valuation-scenario-lab selfcheck", "valuation-scenario-lab selfcheck --root <repo-or-share-root>"],
            ["pyproject.toml", "release/install-smoke-receipt.md"],
        ),
        trouble(
            "finance-boundary-concern",
            "A reviewer is concerned the output could be read as advice or live-data backed.",
            "Inspect safety text and regenerate public artifacts that carry the boundaries.",
            ["valuation-scenario-lab reproducibility-audit --root . --output demo", "valuation-scenario-lab validate-release --root . --format markdown"],
            ["README.md", "demo/reproducibility-audit.html", "skills/agent/valuation-scenario-lab/SKILL.md"],
        ),
    ]
    return {
        "schema_version": "valuation-scenario-lab.troubleshoot.v1.1",
        "generated_on": "static-local",
        "status": "ready" if validation_status == "pass" else "needs diagnostics",
        "release_validation_status": validation_status,
        "guide": problems,
        "boundaries": [
            "No live data.",
            "No broker connections.",
            "No buy/sell/hold advice.",
        ],
    }


def trouble(
    problem_id: str,
    symptom: str,
    diagnostic: str,
    commands: list[str],
    artifacts: list[str],
) -> dict[str, Any]:
    return {
        "id": problem_id,
        "symptom": symptom,
        "diagnostic": diagnostic,
        "commands": commands,
        "artifacts": artifacts,
    }


def troubleshoot_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Troubleshooting Guide",
        "",
        f"Status: {payload['status']}",
        f"Release validation: {payload['release_validation_status']}",
        "",
    ]
    for item in payload["guide"]:
        lines.extend([f"## {item['id']}", "", item["symptom"], "", item["diagnostic"], "", "Commands:", ""])
        lines.extend(f"- `{command}`" for command in item["commands"])
        lines.extend(["", "Artifacts:", ""])
        lines.extend(f"- `{artifact}`" for artifact in item["artifacts"])
        lines.append("")
    lines.extend(["## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def troubleshoot_html(payload: dict[str, Any]) -> str:
    sections = []
    for item in payload["guide"]:
        commands = "".join(f"<li><code>{html.escape(command)}</code></li>" for command in item["commands"])
        artifacts = "".join(f"<li><code>{html.escape(artifact)}</code></li>" for artifact in item["artifacts"])
        sections.append(
            "<section>"
            f"<h2>{html.escape(item['id'])}</h2>"
            f"<p>{html.escape(item['symptom'])}</p>"
            f"<p>{html.escape(item['diagnostic'])}</p>"
            f"<h3>Commands</h3><ul>{commands}</ul>"
            f"<h3>Artifacts</h3><ul>{artifacts}</ul>"
            "</section>"
        )
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Troubleshooting Guide</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
section {{ border-top: 1px solid #d6dde4; padding: 1rem 0; }}
code {{ background: #eef3f8; padding: 0.1rem 0.25rem; }}
</style>
</head>
<body>
<h1>Troubleshooting Guide</h1>
<p>Status: {html.escape(payload['status'])}; release validation: {html.escape(payload['release_validation_status'])}</p>
{''.join(sections)}
<h2>Boundaries</h2><ul>{boundaries}</ul>
</body>
</html>
"""


def readme_snippet_payload(root: Path, output: Path) -> dict[str, Any]:
    packet = read_json(output / "valuation-packet.json")
    artifact_paths = [
        "demo/valuation-packet.html",
        "demo/showcase-dashboard.html",
        "demo/thesis-brief.html",
        "demo/scenario-library.html",
        "demo/casebook.html",
        "demo/reviewer-scorecard.html",
        "demo/troubleshoot.html",
        "demo/reproducibility-audit.html",
        "release/public-bundle.html",
    ]
    quickstart = [
        "python -m venv .venv",
        ". .venv/bin/activate",
        "pip install -e .",
        "valuation-scenario-lab demo",
        "valuation-scenario-lab selfcheck --root .",
    ]
    return {
        "schema_version": "valuation-scenario-lab.readme-snippet.v1.2",
        "generated_on": "static-local",
        "title": "Shortest Public Quickstart Snippet",
        "audience": "new public reader evaluating deterministic local artifacts",
        "quickstart": quickstart,
        "one_line": "Build a deterministic offline valuation scenario packet from fictional local fixtures.",
        "demo_snapshot": {
            "company": packet["company"],
            "ticker": packet["ticker"],
            "weighted_fair_value_per_share": packet["weighted_fair_value_per_share"],
            "margin_of_safety_label": packet["margin_of_safety_label"],
        },
        "artifact_map": [
            {"path": path, "exists": (root / path).exists() or (output / Path(path).name).exists(), "role": readme_artifact_role(path)}
            for path in artifact_paths
        ],
        "boundaries": [
            "No live data.",
            "No broker connections.",
            "No buy/sell/hold advice.",
        ],
    }


def readme_artifact_role(path: str) -> str:
    roles = {
        "demo/valuation-packet.html": "primary packet",
        "demo/showcase-dashboard.html": "visual summary",
        "demo/thesis-brief.html": "analyst narrative",
        "demo/scenario-library.html": "assumption cards",
        "demo/casebook.html": "stranger-readable walkthrough",
        "demo/reviewer-scorecard.html": "reviewer operability",
        "demo/troubleshoot.html": "diagnostic map",
        "demo/reproducibility-audit.html": "repeatability receipt",
        "release/public-bundle.html": "public bundle index",
    }
    return roles.get(path, "public artifact")


def readme_snippet_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Shortest Public Quickstart Snippet",
        "",
        payload["one_line"],
        "",
        "## Quickstart",
        "",
    ]
    lines.extend(f"- `{item}`" for item in payload["quickstart"])
    lines.extend(["", "## Artifact Map", ""])
    lines.extend(
        f"- `{item['path']}`: {item['role']} ({'ok' if item['exists'] else 'missing'})"
        for item in payload["artifact_map"]
    )
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines) + "\n"


def readme_snippet_html(payload: dict[str, Any]) -> str:
    commands = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in payload["quickstart"])
    artifacts = "".join(
        "<li>"
        f"<code>{html.escape(item['path'])}</code>"
        f"<span>{html.escape(item['role'])}</span>"
        f"<strong>{'ok' if item['exists'] else 'missing'}</strong>"
        "</li>"
        for item in payload["artifact_map"]
    )
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Shortest Public Quickstart Snippet</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
main {{ max-width: 860px; }}
li {{ margin: 0.4rem 0; }}
code {{ background: #eef3f8; padding: 0.1rem 0.25rem; }}
.artifacts li {{ display: grid; grid-template-columns: minmax(220px, 1fr) 1fr auto; gap: 0.75rem; border-top: 1px solid #d6dde4; padding-top: 0.45rem; }}
</style>
</head>
<body>
<main>
<h1>{html.escape(payload['title'])}</h1>
<p>{html.escape(payload['one_line'])}</p>
<p>{html.escape(payload['demo_snapshot']['company'])} ({html.escape(payload['demo_snapshot']['ticker'])}) static fixture snapshot.</p>
<h2>Quickstart</h2>
<ol>{commands}</ol>
<h2>Artifact Map</h2>
<ul class="artifacts">{artifacts}</ul>
<h2>Boundaries</h2>
<ul>{boundaries}</ul>
</main>
</body>
</html>
"""


def release_deck_payload(root: Path, output: Path) -> dict[str, Any]:
    packet = read_json(output / "valuation-packet.json")
    snippet = read_json(output / "readme-snippet.json") if (output / "readme-snippet.json").exists() else readme_snippet_payload(root, output)
    scorecard = read_json(output / "reviewer-scorecard.json") if (output / "reviewer-scorecard.json").exists() else {"score": 0, "status": "missing"}
    slides = [
        release_slide(
            "problem",
            "Problem",
            "Public valuation demos often mix assumptions, narrative, and execution context.",
            ["Readers need static artifacts they can inspect without accounts, feeds, or scripts.", "Reviewers need boundaries and evidence in the same release tree."],
            ["README.md", "docs/release-checks.md"],
        ),
        release_slide(
            "user",
            "User",
            "Research-oriented investors, analysts, and agent builders evaluating local assumptions.",
            ["The user starts with fictional JSON fixtures.", "The user reviews deterministic Markdown, JSON, HTML, and SVG outputs."],
            ["examples/company.json", "examples/software-compounder.json"],
        ),
        release_slide(
            "workflow",
            "Workflow",
            "One command builds the public demo tree and release receipts.",
            snippet["quickstart"],
            ["demo/sample-workflow.html", "demo/readme-snippet.html"],
        ),
        release_slide(
            "evidence",
            "Evidence",
            f"The bundled demo for {packet['company']} ({packet['ticker']}) produces a fair value snapshot and reviewer scorecard.",
            [
                f"Weighted fair value per share: {packet['currency']} {packet['weighted_fair_value_per_share']:.2f}.",
                f"Reviewer score: {scorecard.get('score', 0)}/100 ({scorecard.get('status', 'missing')}).",
                "Fixture doctor, reproducibility audit, manifest, and public bundle are checked locally.",
            ],
            ["demo/valuation-packet.html", "demo/reviewer-scorecard.html", "demo/reproducibility-audit.html", "release/public-bundle.html"],
        ),
        release_slide(
            "limitations",
            "Limitations",
            "The project intentionally stops at static research artifacts.",
            ["No live data.", "No broker connections.", "No buy/sell/hold advice."],
            ["README.md", "skills/agent/valuation-scenario-lab/SKILL.md"],
        ),
        release_slide(
            "repeatability",
            "Repeatability",
            "The release is validated by deterministic commands and checked-in artifacts.",
            ["python -m pytest -q", "valuation-scenario-lab selfcheck --root .", "valuation-scenario-lab validate-release --root . --format markdown"],
            ["tests/test_cli.py", "demo/reproducibility-audit.html", "release/release-manifest.json"],
        ),
    ]
    return {
        "schema_version": "valuation-scenario-lab.release-deck.v1.2",
        "generated_on": "static-local",
        "title": "Valuation Scenario Lab v1.2.0 Promotion Deck",
        "format": "static JSON, Markdown, and no-JavaScript HTML",
        "slide_count": len(slides),
        "slides": slides,
        "boundaries": [
            "No live data.",
            "No broker connections.",
            "No buy/sell/hold advice.",
        ],
    }


def release_slide(slug: str, title: str, statement: str, bullets: list[str], artifacts: list[str]) -> dict[str, Any]:
    return {"slug": slug, "title": title, "statement": statement, "bullets": bullets, "artifacts": artifacts}


def release_deck_markdown(payload: dict[str, Any]) -> str:
    lines = [f"# {payload['title']}", "", f"Format: {payload['format']}", ""]
    for index, slide in enumerate(payload["slides"], start=1):
        lines.extend([f"## {index}. {slide['title']}", "", slide["statement"], ""])
        lines.extend(f"- {item}" for item in slide["bullets"])
        lines.extend(["", "Artifacts:"])
        lines.extend(f"- `{item}`" for item in slide["artifacts"])
        lines.append("")
    lines.extend(["## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines) + "\n"


def release_deck_html(payload: dict[str, Any]) -> str:
    sections = []
    for index, slide in enumerate(payload["slides"], start=1):
        bullets = "".join(f"<li>{html.escape(item)}</li>" for item in slide["bullets"])
        artifacts = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in slide["artifacts"])
        sections.append(
            "<section>"
            f"<p class=\"kicker\">{index:02d} / {html.escape(slide['slug'])}</p>"
            f"<h2>{html.escape(slide['title'])}</h2>"
            f"<p class=\"statement\">{html.escape(slide['statement'])}</p>"
            f"<ul>{bullets}</ul>"
            f"<h3>Artifacts</h3><ul>{artifacts}</ul>"
            "</section>"
        )
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(payload['title'])}</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 0; color: #17202a; background: #f6f8fa; }}
main {{ max-width: 980px; margin: 0 auto; padding: 2rem 1rem; }}
header, section {{ background: #ffffff; border: 1px solid #d6dde4; margin: 1rem 0; padding: 1.25rem; }}
h1 {{ margin: 0 0 0.4rem; }}
h2 {{ margin: 0.2rem 0 0.6rem; font-size: 1.8rem; }}
.kicker {{ color: #5d6d7e; text-transform: uppercase; font-size: 0.78rem; }}
.statement {{ font-size: 1.1rem; }}
code {{ background: #eef3f8; padding: 0.1rem 0.25rem; }}
</style>
</head>
<body>
<main>
<header>
<h1>{html.escape(payload['title'])}</h1>
<p>{html.escape(payload['format'])}</p>
</header>
{''.join(sections)}
<section><h2>Boundaries</h2><ul>{boundaries}</ul></section>
</main>
</body>
</html>
"""


def reproducibility_audit_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Reproducibility Audit", "", f"Status: {payload['status']}", "", "## Checks", ""]
    for name, section in payload["checks"].items():
        lines.append(f"- {name.replace('_', ' ')}: {section['status']}")
    manifest = payload["checks"]["hash_manifest_coverage"]
    lines.extend(
        [
            "",
            "## Hash Manifest Coverage",
            "",
            f"- Expected files: {manifest['expected_file_count']}",
            f"- Manifest files: {manifest['manifest_file_count']}",
            f"- Missing: {len(manifest['missing'])}",
            f"- Extra: {len(manifest['extra'])}",
            f"- Hash mismatches: {len(manifest['hash_mismatches'])}",
            "",
            "## Boundaries",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def reproducibility_audit_html(payload: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><td>{html.escape(name.replace('_', ' '))}</td><td>{html.escape(section['status'])}</td></tr>"
        for name, section in payload["checks"].items()
    )
    manifest = payload["checks"]["hash_manifest_coverage"]
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Reproducibility Audit</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
table {{ border-collapse: collapse; width: 100%; max-width: 760px; }}
td, th {{ border: 1px solid #ccd1d1; padding: 0.45rem; text-align: left; }}
code {{ background: #eef3f8; padding: 0.1rem 0.25rem; }}
</style>
</head>
<body>
<h1>Reproducibility Audit</h1>
<p>Status: {html.escape(payload['status'])}</p>
<table><thead><tr><th>Check</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Hash Manifest Coverage</h2>
<ul>
<li>Expected files: {manifest['expected_file_count']}</li>
<li>Manifest files: {manifest['manifest_file_count']}</li>
<li>Missing: {len(manifest['missing'])}</li>
<li>Extra: {len(manifest['extra'])}</li>
<li>Hash mismatches: {len(manifest['hash_mismatches'])}</li>
</ul>
<h2>Boundaries</h2><ul>{boundaries}</ul>
</body>
</html>
"""


def command_install_smoke_receipt(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_dir(output)
    payload = install_smoke_payload(root)
    write_json(output / "install-smoke-receipt.json", payload)
    write_text(output / "install-smoke-receipt.md", install_smoke_markdown(payload))
    write_text(output / "install-smoke-receipt.html", install_smoke_html(payload))
    print(f"wrote {output / 'install-smoke-receipt.json'}")
    return 0


def command_export_bundle(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_dir(output)
    payload = export_bundle_payload(root)
    write_json(output / "public-bundle.json", payload)
    write_text(output / "public-bundle.md", public_bundle_markdown(payload))
    write_text(output / "public-bundle.html", public_bundle_html(payload))
    print(f"wrote {output / 'public-bundle.json'}")
    return 0 if payload["status"] == "pass" else 1


def install_smoke_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Install Smoke Receipt",
        "",
        f"Status: {payload['status']}",
        "",
        payload["network_policy"],
        "",
        "## Install Commands",
        "",
    ]
    for item in payload["install_commands"]:
        lines.append(f"- {item['name']}: `{item['command']}`")
        lines.append(f"  Expected: `{item['expected_output_contains']}`")
    lines.extend(["", "## Entry Point Smoke Commands", ""])
    for item in payload["entry_point_smoke_commands"]:
        lines.append(f"- `{item['command']}`")
        lines.append(f"  Expected: `{item['expected_output_contains']}`")
    lines.extend(["", "## Expected Files", ""])
    lines.extend(f"- `{item['path']}`: {'ok' if item['exists'] else 'missing'}" for item in payload["expected_files"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def install_smoke_html(payload: dict[str, Any]) -> str:
    installs = "".join(
        "<tr>"
        f"<td>{html.escape(item['name'])}</td>"
        f"<td><code>{html.escape(item['command'])}</code></td>"
        f"<td><code>{html.escape(item['expected_output_contains'])}</code></td>"
        "</tr>"
        for item in payload["install_commands"]
    )
    smokes = "".join(
        "<tr>"
        f"<td><code>{html.escape(item['command'])}</code></td>"
        f"<td><code>{html.escape(item['expected_output_contains'])}</code></td>"
        f"<td>{'no' if not item['network_required'] else 'yes'}</td>"
        "</tr>"
        for item in payload["entry_point_smoke_commands"]
    )
    files = "".join(f"<li><code>{html.escape(item['path'])}</code>: {'ok' if item['exists'] else 'missing'}</li>" for item in payload["expected_files"])
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Install Smoke Receipt</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ccd1d1; padding: 0.45rem; text-align: left; vertical-align: top; }}
code {{ background: #eef3f8; padding: 0.1rem 0.25rem; }}
</style>
</head>
<body>
<h1>Install Smoke Receipt</h1>
<p>Status: {html.escape(payload['status'])}</p>
<p>{html.escape(payload['network_policy'])}</p>
<h2>Install Commands</h2>
<table><thead><tr><th>Name</th><th>Command</th><th>Expected Output</th></tr></thead><tbody>{installs}</tbody></table>
<h2>Entry Point Smoke Commands</h2>
<table><thead><tr><th>Command</th><th>Expected Output</th><th>Network</th></tr></thead><tbody>{smokes}</tbody></table>
<h2>Expected Files</h2><ul>{files}</ul>
<h2>Boundaries</h2><ul>{boundaries}</ul>
</body>
</html>
"""


def public_bundle_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Public Bundle Manifest",
        "",
        f"Status: {payload['status']}",
        f"File count: {payload['file_count']}",
        "",
        "## Files",
        "",
        "| Path | Category | SHA-256 | Bytes | Usage |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for item in payload["files"]:
        lines.append(
            f"| `{item['path']}` | {item['category']} | `{item['sha256']}` | {item['bytes']} | {item['usage_note']} |"
        )
    lines.extend(["", "## Self Outputs", ""])
    lines.extend(f"- `{item['path']}`: {item['usage_note']}" for item in payload["self_outputs"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)


def public_bundle_html(payload: dict[str, Any]) -> str:
    rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(item['path'])}</code></td>"
        f"<td>{html.escape(item['category'])}</td>"
        f"<td><code>{html.escape(item['sha256'])}</code></td>"
        f"<td>{item['bytes']}</td>"
        f"<td>{html.escape(item['usage_note'])}</td>"
        "</tr>"
        for item in payload["files"]
    )
    self_outputs = "".join(
        f"<li><code>{html.escape(item['path'])}</code>: {html.escape(item['usage_note'])}</li>"
        for item in payload["self_outputs"]
    )
    boundaries = "".join(f"<li>{html.escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Public Bundle Manifest</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ccd1d1; padding: 0.45rem; text-align: left; vertical-align: top; }}
code {{ background: #eef3f8; padding: 0.1rem 0.25rem; }}
</style>
</head>
<body>
<h1>Public Bundle Manifest</h1>
<p>Status: {html.escape(payload['status'])}; file count: {payload['file_count']}</p>
<table><thead><tr><th>Path</th><th>Category</th><th>SHA-256</th><th>Bytes</th><th>Usage</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Self Outputs</h2><ul>{self_outputs}</ul>
<h2>Boundaries</h2><ul>{boundaries}</ul>
</body>
</html>
"""


def emit_validation(payload: dict, fmt: str) -> int:
    if fmt == "json":
        import json

        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"# {payload.get('schema_version', 'Report')}")
        print()
        print(f"Status: {payload.get('status', 'n/a')}")
        if "score" in payload:
            print(f"Score: {payload['score']}")
        for item in payload.get("findings", payload.get("release_validation", {}).get("findings", [])):
            print(f"- {item['severity']}: {item['message']}")
    return 0 if payload.get("status") in {"pass", "ready"} or payload.get("release_validation", {}).get("status") == "pass" else 1


def command_manifest(root: Path, output: Path) -> int:
    payload = manifest_payload(root)
    ensure_dir(output)
    write_json(output / "release-manifest.json", payload)
    lines = ["# Release Manifest", ""]
    for item in payload["files"]:
        lines.append(f"- `{item['path']}` `{item['sha256']}` {item['bytes']} bytes")
    write_text(output / "release-manifest.md", "\n".join(lines))
    print(f"wrote {output / 'release-manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
