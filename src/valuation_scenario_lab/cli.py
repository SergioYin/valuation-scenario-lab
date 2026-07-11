from __future__ import annotations

import argparse
import html
import sys
import sysconfig
import tempfile
from pathlib import Path

from . import __version__
from .engine import build_decision_journal, build_packet, build_review_ledger, compare_packets, sensitivity_matrix, validate_company
from .io import ensure_dir, read_json, write_json, write_text
from .release import maturity_report as maturity_payload
from .release import release_manifest as manifest_payload
from .release import validate_release as validate_release_payload
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

    receipt = sub.add_parser("visual-receipt")
    receipt.add_argument("--root", default=".")
    receipt.add_argument("--output", default="demo")

    validate = sub.add_parser("validate-release")
    validate.add_argument("--root", default=".")
    validate.add_argument("--format", choices=["json", "markdown"], default="json")

    maturity = sub.add_parser("maturity-report")
    maturity.add_argument("--root", default=".")
    maturity.add_argument("--format", choices=["json", "markdown"], default="json")

    manifest = sub.add_parser("release-manifest")
    manifest.add_argument("--root", default=".")
    manifest.add_argument("--output", default="release")

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
        if args.command == "decision-journal":
            return command_decision_journal(Path(args.packet), Path(args.ledger), Path(args.output))
        if args.command == "public-readiness-landing":
            return command_public_readiness_landing(Path(args.root), Path(args.output))
        if args.command == "selfcheck":
            return command_selfcheck(Path(args.root) if args.root else None)
        if args.command == "quickstart-check":
            return command_quickstart_check(Path(args.root), Path(args.output))
        if args.command == "visual-receipt":
            return command_visual_receipt(Path(args.root), Path(args.output))
        if args.command == "validate-release":
            return emit_validation(validate_release_payload(Path(args.root)), args.format)
        if args.command == "maturity-report":
            return emit_validation(maturity_payload(Path(args.root)), args.format)
        if args.command == "release-manifest":
            return command_manifest(Path(args.root), Path(args.output))
        if args.command == "demo":
            root = Path(args.root)
            command_build_packet(root / "examples", root / "demo")
            command_compare_history(root / "demo" / "valuation-packet.json", root / "examples" / "prior-packet.json", root / "demo")
            command_review_ledger(root / "demo" / "valuation-packet.json", root / "examples" / "review-policy.json", root / "demo")
            command_sensitivity(root / "examples", root / "demo")
            command_decision_journal(root / "demo" / "valuation-packet.json", root / "demo" / "review-ledger.json", root / "demo")
            command_public_readiness_landing(root, root / "demo")
            command_quickstart_check(root, root / "demo")
            command_visual_receipt(root, root / "demo")
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
    packet = read_json(output / "valuation-packet.json")
    payload = public_readiness_payload(packet)
    write_json(output / "public-readiness-landing.json", payload)
    write_text(output / "public-readiness-landing.md", public_readiness_markdown(payload))
    write_text(output / "public-readiness-landing.html", public_readiness_html(payload))
    print(f"wrote {output / 'public-readiness-landing.html'}")
    return 0


def command_selfcheck(root_arg: Path | None = None) -> int:
    root = resolve_root(root_arg)
    findings = validate_company(read_json(root / "examples" / "company.json"))
    if findings:
        for item in findings:
            print(f"FAIL {item}")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        command_build_packet(root / "examples", out)
        command_compare_history(out / "valuation-packet.json", root / "examples" / "prior-packet.json", out)
        command_review_ledger(out / "valuation-packet.json", root / "examples" / "review-policy.json", out)
        command_sensitivity(root / "examples", out)
        command_decision_journal(out / "valuation-packet.json", out / "review-ledger.json", out)
        command_public_readiness_landing(root, out)
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
        "decision-journal.json",
        "decision-journal.md",
        "public-readiness-landing.json",
        "public-readiness-landing.md",
        "public-readiness-landing.html",
    ]
    files = [{"path": f"demo/{name}", "exists": (output / name).exists()} for name in expected]
    payload = {
        "schema_version": "valuation-scenario-lab.quickstart-check.v0.3",
        "status": "pass" if all(item["exists"] for item in files) else "fail",
        "fixture_source": "local-or-packaged-fixtures",
        "commands": [
            "valuation-scenario-lab demo",
            "valuation-scenario-lab selfcheck --root .",
            "valuation-scenario-lab quickstart-check --root . --output demo",
            "valuation-scenario-lab visual-receipt --root . --output demo",
            "valuation-scenario-lab decision-journal --packet demo/valuation-packet.json --ledger demo/review-ledger.json --output demo",
            "valuation-scenario-lab public-readiness-landing --root . --output demo",
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
    print(f"wrote {output / 'quickstart-check.json'}")
    return 0 if payload["status"] == "pass" else 1


def command_visual_receipt(root: Path, output: Path) -> int:
    root = resolve_root(root)
    ensure_demo_artifacts(root, output)
    packet = read_json(output / "valuation-packet.json")
    payload = {
        "schema_version": "valuation-scenario-lab.visual-receipt.v0.3",
        "company": packet["company"],
        "ticker": packet["ticker"],
        "weighted_fair_value_per_share": packet["weighted_fair_value_per_share"],
        "weighted_range_per_share": packet["weighted_range_per_share"],
        "margin_of_safety_label": packet["margin_of_safety_label"],
        "weighted_margin_of_safety_pct": packet["weighted_margin_of_safety_pct"],
        "artifact_count": 14,
        "boundaries": packet["boundaries"],
    }
    write_json(output / "visual-receipt.json", payload)
    write_text(output / "visual-receipt.md", visual_receipt_markdown(payload))
    write_text(output / "visual-receipt.html", visual_receipt_html(payload))
    print(f"wrote {output / 'visual-receipt.html'}")
    return 0


def ensure_demo_artifacts(root: Path, output: Path) -> None:
    command_build_packet(root / "examples", output)
    command_compare_history(output / "valuation-packet.json", root / "examples" / "prior-packet.json", output)
    command_review_ledger(output / "valuation-packet.json", root / "examples" / "review-policy.json", output)
    command_sensitivity(root / "examples", output)
    command_decision_journal(output / "valuation-packet.json", output / "review-ledger.json", output)


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
        "schema_version": "valuation-scenario-lab.public-readiness.v0.3",
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
        ],
        "demo_company": packet.get("company"),
        "demo_ticker": packet.get("ticker"),
        "demo_outputs": [
            "demo/valuation-packet.html",
            "demo/quickstart-check.md",
            "demo/visual-receipt.html",
            "demo/decision-journal.md",
            "demo/public-readiness-landing.html",
        ],
        "readiness_checks": [
            "zero runtime dependencies",
            "static local fixtures",
            "deterministic demo artifacts",
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
