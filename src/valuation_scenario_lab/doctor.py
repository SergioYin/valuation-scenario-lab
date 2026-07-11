from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from .model import as_float

DOCTOR_SCHEMA_VERSION = "valuation-scenario-lab.fixture-doctor.v0.5"
COMPANY_FIXTURE_SKIP = {"prior-packet.json", "review-policy.json"}
TOP_LEVEL_NUMERIC_FIELDS = ["current_price", "shares_outstanding_m", "net_cash_m"]
SCENARIO_NUMERIC_FIELDS = [
    "weight",
    "starting_revenue_m",
    "revenue_growth_pct",
    "fcf_margin_pct",
    "discount_rate_pct",
    "terminal_growth_pct",
    "terminal_multiple",
]


def fixture_doctor(fixtures: Path, policy: dict[str, Any] | None = None) -> dict[str, Any]:
    freshness_limit_days = as_float((policy or {}).get("freshness_limit_days", 45), "freshness_limit_days")
    issues: list[dict[str, Any]] = []
    files = []
    for path in sorted(fixtures.glob("*.json")):
        if path.name in COMPANY_FIXTURE_SKIP:
            continue
        rel = public_fixture_path(path, fixtures)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except JSONDecodeError as exc:
            issues.append(issue("error", "schema", rel, "$", f"invalid JSON: {exc.msg}"))
            files.append({"path": rel, "status": "fail"})
            continue
        if not isinstance(payload, dict):
            issues.append(issue("error", "schema", rel, "$", "fixture must contain a JSON object"))
            files.append({"path": rel, "status": "fail"})
            continue
        before = len(issues)
        inspect_company_fixture(payload, rel, freshness_limit_days, issues)
        file_errors = any(item["severity"] == "error" for item in issues[before:])
        files.append({"path": rel, "status": "fail" if file_errors else "pass"})
    if not files:
        issues.append(issue("error", "schema", fixtures.as_posix(), "$", "no company fixture JSON files found"))
    status = "fail" if any(item["severity"] == "error" for item in issues) else "pass"
    return {
        "schema_version": DOCTOR_SCHEMA_VERSION,
        "generated_on": "static-local",
        "status": status,
        "fixture_count": len(files),
        "freshness_limit_days": int(freshness_limit_days) if freshness_limit_days.is_integer() else freshness_limit_days,
        "files": files,
        "issue_count": len(issues),
        "issues": issues,
        "boundaries": [
            "No live data.",
            "No broker connections.",
            "No buy/sell/hold advice.",
        ],
    }


def inspect_company_fixture(payload: dict[str, Any], file_path: str, freshness_limit_days: float, issues: list[dict[str, Any]]) -> None:
    required = ["company", "current_price", "shares_outstanding_m", "net_cash_m", "scenarios"]
    for field in required:
        if field not in payload:
            issues.append(issue("error", "schema", file_path, f"$.{field}", f"missing required field: {field}"))
    for field in TOP_LEVEL_NUMERIC_FIELDS:
        check_numeric(payload, field, file_path, f"$.{field}", issues)
    check_freshness_entries(payload.get("source_freshness"), file_path, "$.source_freshness", freshness_limit_days, issues)
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        issues.append(issue("error", "schema", file_path, "$.scenarios", "scenarios must be a non-empty list"))
        return
    total_weight = 0.0
    saw_weight_error = False
    for index, scenario in enumerate(scenarios):
        scenario_path = f"$.scenarios[{index}]"
        if not isinstance(scenario, dict):
            issues.append(issue("error", "schema", file_path, scenario_path, "scenario must be an object"))
            saw_weight_error = True
            continue
        for field in ["name", *SCENARIO_NUMERIC_FIELDS]:
            if field not in scenario:
                issues.append(issue("error", "schema", file_path, f"{scenario_path}.{field}", f"scenario missing {field}"))
        for field in SCENARIO_NUMERIC_FIELDS:
            numeric = check_numeric(scenario, field, file_path, f"{scenario_path}.{field}", issues)
            if field == "weight":
                if numeric is None:
                    saw_weight_error = True
                else:
                    total_weight += numeric
                    if numeric < 0 or numeric > 1:
                        saw_weight_error = True
                        issues.append(issue("error", "weight", file_path, f"{scenario_path}.weight", "scenario weight must be between 0 and 1"))
        check_freshness_entries(scenario.get("source_freshness"), file_path, f"{scenario_path}.source_freshness", freshness_limit_days, issues)
    if not saw_weight_error and abs(total_weight - 1.0) > 0.001:
        issues.append(issue("error", "weight", file_path, "$.scenarios", f"scenario weights must sum to 1.0; got {total_weight:.3f}"))


def check_numeric(payload: dict[str, Any], field: str, file_path: str, json_path: str, issues: list[dict[str, Any]]) -> float | None:
    if field not in payload:
        return None
    try:
        return as_float(payload[field], field)
    except ValueError:
        issues.append(issue("error", "numeric", file_path, json_path, f"{field} must be numeric"))
        return None


def check_freshness_entries(
    entries: Any,
    file_path: str,
    json_path: str,
    freshness_limit_days: float,
    issues: list[dict[str, Any]],
) -> None:
    if entries is None:
        issues.append(issue("warning", "staleness", file_path, json_path, "source_freshness is missing"))
        return
    if not isinstance(entries, list):
        issues.append(issue("error", "schema", file_path, json_path, "source_freshness must be a list"))
        return
    for index, entry in enumerate(entries):
        entry_path = f"{json_path}[{index}]"
        if not isinstance(entry, dict):
            issues.append(issue("error", "schema", file_path, entry_path, "source_freshness entry must be an object"))
            continue
        age = check_numeric(entry, "age_days", file_path, f"{entry_path}.age_days", issues)
        if age is not None and age > freshness_limit_days:
            issues.append(
                issue(
                    "warning",
                    "staleness",
                    file_path,
                    f"{entry_path}.age_days",
                    f"source age {age:.0f} days exceeds freshness limit {freshness_limit_days:.0f}",
                )
            )


def issue(severity: str, category: str, file_path: str, json_path: str, message: str) -> dict[str, str]:
    return {
        "severity": severity,
        "category": category,
        "file": file_path,
        "path": json_path,
        "message": message,
    }


def public_fixture_path(path: Path, fixtures: Path) -> str:
    try:
        return path.relative_to(fixtures.parent).as_posix()
    except ValueError:
        return path.name


def fixture_doctor_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Fixture Doctor",
        "",
        f"Status: {payload['status']}",
        f"Fixture count: {payload['fixture_count']}",
        f"Freshness limit days: {payload['freshness_limit_days']}",
        "",
        "## Files",
        "",
    ]
    lines.extend(f"- `{item['path']}`: {item['status']}" for item in payload["files"])
    lines.extend(["", "## Issues", ""])
    if payload["issues"]:
        lines.extend(
            f"- {item['severity']} {item['category']} `{item['file']}` `{item['path']}`: {item['message']}"
            for item in payload["issues"]
        )
    else:
        lines.append("- none")
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines)
