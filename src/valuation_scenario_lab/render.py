from __future__ import annotations

import html
from typing import Any


def packet_markdown(packet: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| {item['scenario']} | {item['weight']:.3f} | {item['low']:.2f} | {item['base']:.2f} | {item['high']:.2f} | {item['margin_label']} |"
        for item in packet["valuation_ranges"]
    )
    prompts = "\n".join(f"- {item}" for item in packet["review_prompts"])
    boundaries = "\n".join(f"- {item}" for item in packet["boundaries"])
    return f"""# Valuation Scenario Packet

Company: {packet['company']} ({packet['ticker']})

Weighted fair value per share: {packet['currency']} {packet['weighted_fair_value_per_share']:.2f}
Weighted range per share: {packet['currency']} {packet['weighted_range_per_share'][0]:.2f} to {packet['currency']} {packet['weighted_range_per_share'][1]:.2f}
Margin-of-safety label: {packet['margin_of_safety_label']} ({packet['weighted_margin_of_safety_pct']:.1f}%)

| Scenario | Weight | Low | Base | High | Label |
| --- | ---: | ---: | ---: | ---: | --- |
{rows}

## Review Prompts

{prompts}

## Boundaries

{boundaries}
"""


def simple_markdown(title: str, payload: dict[str, Any]) -> str:
    lines = [f"# {title}", "", f"Schema: `{payload.get('schema_version', 'n/a')}`", ""]
    if "changes" in payload:
        lines.extend(["## Changes", ""])
        for item in payload["changes"]:
            lines.append(f"- {item['field']}: {item['prior']} -> {item['current']}")
    if "scenario_changes" in payload:
        lines.extend(["", "## Scenario Changes", ""])
        for item in payload["scenario_changes"]:
            lines.append(f"- {item['scenario']}: {item.get('prior_base')} -> {item.get('current_base')} (delta {item.get('delta')})")
    if "entries" in payload:
        lines.extend(["## Ledger Entries", ""])
        for item in payload["entries"]:
            lines.append(f"- {item['priority']}: {item['scenario']} - {item['review_question']}")
    if "rows" in payload:
        lines.extend(["## Matrix", "", "| Discount Delta | Margin Delta | Fair Value | MOS |", "| ---: | ---: | ---: | ---: |"])
        for item in payload["rows"]:
            lines.append(
                f"| {item['discount_delta_pct']:.1f} | {item['fcf_margin_delta_pct']:.1f} | {item['weighted_fair_value_per_share']:.2f} | {item['weighted_margin_of_safety_pct']:.1f}% |"
            )
    lines.extend(["", "## Boundaries", ""])
    for item in payload.get("boundaries", []):
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def packet_html(packet: dict[str, Any]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(item['scenario'])}</td>"
        f"<td>{item['weight']:.3f}</td>"
        f"<td>{item['low']:.2f}</td>"
        f"<td>{item['base']:.2f}</td>"
        f"<td>{item['high']:.2f}</td>"
        f"<td>{html.escape(item['margin_label'])}</td>"
        "</tr>"
        for item in packet["valuation_ranges"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Valuation Scenario Packet</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ccd1d1; padding: 0.45rem; text-align: left; }}
.badge {{ display: inline-block; border: 1px solid #5d6d7e; padding: 0.2rem 0.45rem; }}
</style>
</head>
<body>
<h1>{html.escape(packet['company'])} Valuation Scenario Packet</h1>
<p class="badge">Research only; no advice or execution.</p>
<p>Weighted fair value per share: {packet['currency']} {packet['weighted_fair_value_per_share']:.2f}</p>
<p>Weighted margin-of-safety label: {html.escape(packet['margin_of_safety_label'])} ({packet['weighted_margin_of_safety_pct']:.1f}%)</p>
<table><thead><tr><th>Scenario</th><th>Weight</th><th>Low</th><th>Base</th><th>High</th><th>Label</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Boundaries</h2>
<ul>{"".join(f"<li>{html.escape(item)}</li>" for item in packet["boundaries"])}</ul>
</body>
</html>
"""
