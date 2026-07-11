from __future__ import annotations

import argparse
import html
import sys
import sysconfig
import tempfile
from pathlib import Path

from . import __version__
from .engine import (
    assumption_change_walkthrough,
    build_decision_journal,
    build_packet,
    build_review_ledger,
    compare_packets,
    demo_gallery,
    sensitivity_matrix,
    validate_company,
)
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
            command_assumption_walkthrough(root / "examples", root / "demo", None, "fcf_margin_pct", 2.0)
            command_demo_gallery(root / "examples", root / "demo")
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
        command_assumption_walkthrough(root / "examples", out, None, "fcf_margin_pct", 2.0)
        command_demo_gallery(root / "examples", out)
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
    ]
    files = [{"path": f"demo/{name}", "exists": (output / name).exists()} for name in expected]
    payload = {
        "schema_version": "valuation-scenario-lab.quickstart-check.v0.4",
        "status": "pass" if all(item["exists"] for item in files) else "fail",
        "fixture_source": "local-or-packaged-fixtures",
        "commands": [
            "valuation-scenario-lab demo",
            "valuation-scenario-lab selfcheck --root .",
            "valuation-scenario-lab quickstart-check --root . --output demo",
            "valuation-scenario-lab visual-receipt --root . --output demo",
            "valuation-scenario-lab assumption-change-walkthrough --fixtures examples --output demo",
            "valuation-scenario-lab demo-gallery --fixtures examples --output demo",
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
        "schema_version": "valuation-scenario-lab.visual-receipt.v0.4",
        "company": packet["company"],
        "ticker": packet["ticker"],
        "weighted_fair_value_per_share": packet["weighted_fair_value_per_share"],
        "weighted_range_per_share": packet["weighted_range_per_share"],
        "margin_of_safety_label": packet["margin_of_safety_label"],
        "weighted_margin_of_safety_pct": packet["weighted_margin_of_safety_pct"],
        "artifact_count": 20,
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
    command_assumption_walkthrough(root / "examples", output, None, "fcf_margin_pct", 2.0)
    command_demo_gallery(root / "examples", output)
    command_decision_journal(output / "valuation-packet.json", output / "review-ledger.json", output)


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
        "schema_version": "valuation-scenario-lab.public-readiness.v0.4",
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
            "demo/assumption-change-walkthrough.html",
            "demo/multi-company-demo-gallery.html",
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
