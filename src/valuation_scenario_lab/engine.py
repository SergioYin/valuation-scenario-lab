from __future__ import annotations

from datetime import date
from typing import Any

from .model import BOUNDARIES, ScenarioResult, as_float

PACKET_SCHEMA_VERSION = "valuation-scenario-lab.v0.5"


def validate_company(company: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    required = ["company", "current_price", "shares_outstanding_m", "net_cash_m", "scenarios"]
    for field in required:
        if field not in company:
            findings.append(f"missing required field: {field}")
    for field in ["current_price", "shares_outstanding_m", "net_cash_m"]:
        if field in company:
            try:
                as_float(company[field], field)
            except ValueError as exc:
                findings.append(str(exc))
    scenarios = company.get("scenarios", [])
    if not isinstance(scenarios, list) or not scenarios:
        findings.append("scenarios must be a non-empty list")
        return findings
    total_weight = 0.0
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            findings.append(f"scenario {index} must be an object")
            continue
        for field in [
            "name",
            "weight",
            "starting_revenue_m",
            "revenue_growth_pct",
            "fcf_margin_pct",
            "discount_rate_pct",
            "terminal_growth_pct",
            "terminal_multiple",
        ]:
            if field not in scenario:
                findings.append(f"scenario {index} missing {field}")
        if "weight" in scenario:
            try:
                total_weight += as_float(scenario["weight"], f"scenario {index} weight")
            except ValueError as exc:
                findings.append(str(exc))
    if scenarios and abs(total_weight - 1.0) > 0.001:
        findings.append(f"scenario weights must sum to 1.0; got {total_weight:.3f}")
    return findings


def build_packet(company: dict[str, Any]) -> dict[str, Any]:
    findings = validate_company(company)
    if findings:
        raise ValueError("; ".join(findings))

    current_price = as_float(company["current_price"], "current_price")
    shares = as_float(company["shares_outstanding_m"], "shares_outstanding_m")
    net_cash = as_float(company["net_cash_m"], "net_cash_m")
    results = [_scenario_result(item, shares, net_cash, current_price) for item in company["scenarios"]]
    weighted_fair_value = sum(item.weight * item.blended_value_per_share for item in results)
    weighted_low = sum(item.weight * item.low_value_per_share for item in results)
    weighted_high = sum(item.weight * item.high_value_per_share for item in results)
    weighted_mos = (weighted_fair_value - current_price) / current_price * 100.0
    label = margin_label(weighted_mos)
    return {
        "schema_version": PACKET_SCHEMA_VERSION,
        "generated_on": "static-local",
        "company": company["company"],
        "ticker": company.get("ticker", "LOCAL"),
        "currency": company.get("currency", "USD"),
        "current_price": round(current_price, 2),
        "weighted_fair_value_per_share": round(weighted_fair_value, 2),
        "weighted_range_per_share": [round(weighted_low, 2), round(weighted_high, 2)],
        "weighted_margin_of_safety_pct": round(weighted_mos, 1),
        "margin_of_safety_label": label,
        "valuation_ranges": [
            {
                "scenario": item.name,
                "weight": round(item.weight, 3),
                "low": round(item.low_value_per_share, 2),
                "base": round(item.blended_value_per_share, 2),
                "high": round(item.high_value_per_share, 2),
                "margin_of_safety_pct": round(item.margin_of_safety_pct, 1),
                "margin_label": item.margin_label,
                "score": round(item.score, 2),
            }
            for item in results
        ],
        "catalysts": sorted({entry for item in company["scenarios"] for entry in item.get("catalysts", [])}),
        "risks": sorted({entry for item in company["scenarios"] for entry in item.get("risks", [])}),
        "source_freshness": company.get("source_freshness", []),
        "review_prompts": review_prompts(company, weighted_mos),
        "boundaries": BOUNDARIES,
    }


def _scenario_result(scenario: dict[str, Any], shares: float, net_cash: float, current_price: float) -> ScenarioResult:
    revenue = as_float(scenario["starting_revenue_m"], "starting_revenue_m")
    growth = as_float(scenario["revenue_growth_pct"], "revenue_growth_pct") / 100.0
    margin = as_float(scenario["fcf_margin_pct"], "fcf_margin_pct") / 100.0
    discount = as_float(scenario["discount_rate_pct"], "discount_rate_pct") / 100.0
    terminal_growth = as_float(scenario["terminal_growth_pct"], "terminal_growth_pct") / 100.0
    terminal_multiple = as_float(scenario["terminal_multiple"], "terminal_multiple")
    pv_fcf = 0.0
    final_fcf = 0.0
    for year in range(1, 6):
        year_revenue = revenue * ((1.0 + growth) ** year)
        final_fcf = year_revenue * margin
        pv_fcf += final_fcf / ((1.0 + discount) ** year)
    terminal_dcf = final_fcf * (1.0 + terminal_growth) / max(discount - terminal_growth, 0.01)
    terminal_multiple_value = final_fcf * terminal_multiple
    dcf_per_share = (pv_fcf + terminal_dcf + net_cash) / shares
    multiple_per_share = (pv_fcf + terminal_multiple_value + net_cash) / shares
    blended = (dcf_per_share * 0.7) + (multiple_per_share * 0.3)
    mos = (blended - current_price) / current_price * 100.0
    freshness_days = max([as_float(item.get("age_days", 0), "age_days") for item in scenario.get("source_freshness", [])] or [0])
    score = mos - (freshness_days / 10.0)
    return ScenarioResult(
        name=str(scenario["name"]),
        weight=as_float(scenario["weight"], "weight"),
        intrinsic_value_per_share=dcf_per_share,
        multiple_cross_check_per_share=multiple_per_share,
        blended_value_per_share=blended,
        low_value_per_share=blended * 0.9,
        high_value_per_share=blended * 1.1,
        margin_of_safety_pct=mos,
        margin_label=margin_label(mos),
        score=score,
    )


def margin_label(mos_pct: float) -> str:
    if mos_pct >= 25:
        return "large positive gap"
    if mos_pct >= 10:
        return "moderate positive gap"
    if mos_pct >= -10:
        return "near modeled value"
    if mos_pct >= -25:
        return "moderate negative gap"
    return "large negative gap"


def review_prompts(company: dict[str, Any], weighted_mos: float) -> list[str]:
    prompts = [
        "Confirm that all assumptions are sourced from local research notes.",
        "Review whether scenario weights still reflect the written thesis.",
    ]
    if abs(weighted_mos) > 20:
        prompts.append("Document why the modeled value gap is large before using this packet in discussion.")
    if company.get("source_freshness"):
        prompts.append("Refresh any source with an age_days value above the local review policy.")
    return prompts


def compare_packets(current: dict[str, Any], prior: dict[str, Any]) -> dict[str, Any]:
    fields = [
        "weighted_fair_value_per_share",
        "weighted_margin_of_safety_pct",
        "margin_of_safety_label",
    ]
    changes = []
    for field in fields:
        changes.append({"field": field, "prior": prior.get(field), "current": current.get(field)})
    prior_ranges = {item["scenario"]: item for item in prior.get("valuation_ranges", [])}
    scenario_changes = []
    for item in current.get("valuation_ranges", []):
        prior_item = prior_ranges.get(item["scenario"], {})
        scenario_changes.append(
            {
                "scenario": item["scenario"],
                "prior_base": prior_item.get("base"),
                "current_base": item.get("base"),
                "delta": round(float(item.get("base", 0)) - float(prior_item.get("base", 0)), 2) if prior_item else None,
            }
        )
    return {
        "schema_version": "valuation-scenario-lab.compare.v0.5",
        "generated_on": "static-local",
        "company": current.get("company"),
        "changes": changes,
        "scenario_changes": scenario_changes,
        "boundaries": BOUNDARIES,
    }


def build_review_ledger(packet: dict[str, Any], policy: dict[str, Any] | None = None) -> dict[str, Any]:
    threshold = float((policy or {}).get("high_priority_abs_mos_pct", 20))
    entries = []
    for item in packet.get("valuation_ranges", []):
        priority = "high" if abs(float(item.get("margin_of_safety_pct", 0))) >= threshold else "normal"
        entries.append(
            {
                "scenario": item["scenario"],
                "priority": priority,
                "margin_label": item["margin_label"],
                "review_question": f"Which assumption would most change the {item['scenario']} valuation range?",
                "owner": (policy or {}).get("owner_placeholder", "research reviewer"),
                "evidence": ["valuation-packet.json"],
            }
        )
    return {
        "schema_version": "valuation-scenario-lab.ledger.v0.5",
        "generated_on": "static-local",
        "company": packet.get("company"),
        "entries": entries,
        "boundaries": BOUNDARIES,
    }


def build_decision_journal(packet: dict[str, Any], ledger: dict[str, Any] | None = None) -> dict[str, Any]:
    entries = []
    for index, item in enumerate(packet.get("valuation_ranges", []), start=1):
        entries.append(
            {
                "id": f"DJ-{index:03d}",
                "scenario": item["scenario"],
                "decision": "recorded for research review",
                "rationale": f"Modeled range carries a {item['margin_label']} label at {item['margin_of_safety_pct']:.1f}%.",
                "evidence": ["valuation-packet.json", "review-ledger.json"],
                "next_review": "refresh local assumptions before external discussion",
            }
        )
    open_questions = [
        entry["review_question"]
        for entry in (ledger or {}).get("entries", [])
        if isinstance(entry, dict) and entry.get("review_question")
    ]
    return {
        "schema_version": "valuation-scenario-lab.decision-journal.v0.5",
        "generated_on": "static-local",
        "company": packet.get("company"),
        "ticker": packet.get("ticker"),
        "current_price": packet.get("current_price"),
        "weighted_fair_value_per_share": packet.get("weighted_fair_value_per_share"),
        "weighted_margin_of_safety_pct": packet.get("weighted_margin_of_safety_pct"),
        "summary_decision": "research packet logged; no action recommendation",
        "journal_entries": entries,
        "open_questions": open_questions,
        "boundaries": BOUNDARIES,
    }


def sensitivity_matrix(company: dict[str, Any]) -> dict[str, Any]:
    base = build_packet(company)
    rows = []
    original = company["scenarios"][0]
    for discount_delta in [-1.0, 0.0, 1.0]:
        for margin_delta in [-2.0, 0.0, 2.0]:
            clone = {**company, "scenarios": [dict(item) for item in company["scenarios"]]}
            clone["scenarios"][0] = {**original}
            clone["scenarios"][0]["discount_rate_pct"] = float(original["discount_rate_pct"]) + discount_delta
            clone["scenarios"][0]["fcf_margin_pct"] = float(original["fcf_margin_pct"]) + margin_delta
            packet = build_packet(clone)
            rows.append(
                {
                    "discount_delta_pct": discount_delta,
                    "fcf_margin_delta_pct": margin_delta,
                    "weighted_fair_value_per_share": packet["weighted_fair_value_per_share"],
                    "weighted_margin_of_safety_pct": packet["weighted_margin_of_safety_pct"],
                }
            )
    return {
        "schema_version": "valuation-scenario-lab.sensitivity.v0.5",
        "generated_on": "static-local",
        "company": base["company"],
        "base_weighted_fair_value_per_share": base["weighted_fair_value_per_share"],
        "rows": rows,
        "boundaries": BOUNDARIES,
    }


def assumption_change_walkthrough(
    company: dict[str, Any],
    scenario_name: str | None = None,
    field: str = "fcf_margin_pct",
    delta: float = 2.0,
) -> dict[str, Any]:
    base_packet = build_packet(company)
    scenario_index = scenario_index_for(company, scenario_name)
    base_scenario = company["scenarios"][scenario_index]
    if field not in base_scenario:
        raise ValueError(f"scenario does not contain assumption field: {field}")
    original_value = as_float(base_scenario[field], field)
    changed_company = {**company, "scenarios": [dict(item) for item in company["scenarios"]]}
    changed_company["scenarios"][scenario_index][field] = original_value + delta
    changed_packet = build_packet(changed_company)
    return {
        "schema_version": "valuation-scenario-lab.assumption-change.v0.5",
        "generated_on": "static-local",
        "company": base_packet["company"],
        "ticker": base_packet["ticker"],
        "scenario": str(base_scenario["name"]),
        "changed_assumption": field,
        "prior_value": round(original_value, 4),
        "new_value": round(original_value + delta, 4),
        "delta": round(delta, 4),
        "before": {
            "weighted_fair_value_per_share": base_packet["weighted_fair_value_per_share"],
            "weighted_margin_of_safety_pct": base_packet["weighted_margin_of_safety_pct"],
            "margin_of_safety_label": base_packet["margin_of_safety_label"],
        },
        "after": {
            "weighted_fair_value_per_share": changed_packet["weighted_fair_value_per_share"],
            "weighted_margin_of_safety_pct": changed_packet["weighted_margin_of_safety_pct"],
            "margin_of_safety_label": changed_packet["margin_of_safety_label"],
        },
        "movement": {
            "weighted_fair_value_per_share": round(
                changed_packet["weighted_fair_value_per_share"] - base_packet["weighted_fair_value_per_share"], 2
            ),
            "weighted_margin_of_safety_pct": round(
                changed_packet["weighted_margin_of_safety_pct"] - base_packet["weighted_margin_of_safety_pct"], 1
            ),
        },
        "walkthrough_steps": [
            "Start with the checked local fixture.",
            f"Change {field} for the selected scenario only.",
            "Rebuild the deterministic packet with the same model.",
            "Compare weighted fair value, margin label, and margin-of-safety movement.",
            "Record the result as research review evidence, not as an action recommendation.",
        ],
        "boundaries": BOUNDARIES,
    }


def scenario_index_for(company: dict[str, Any], scenario_name: str | None) -> int:
    if scenario_name is None:
        return 0
    for index, scenario in enumerate(company.get("scenarios", [])):
        if scenario.get("name") == scenario_name:
            return index
    raise ValueError(f"unknown scenario: {scenario_name}")


def demo_gallery(companies: list[dict[str, Any]]) -> dict[str, Any]:
    packets = [build_packet(company) for company in companies]
    cards = []
    for packet in packets:
        cards.append(
            {
                "company": packet["company"],
                "ticker": packet["ticker"],
                "currency": packet["currency"],
                "weighted_fair_value_per_share": packet["weighted_fair_value_per_share"],
                "weighted_range_per_share": packet["weighted_range_per_share"],
                "weighted_margin_of_safety_pct": packet["weighted_margin_of_safety_pct"],
                "margin_of_safety_label": packet["margin_of_safety_label"],
                "scenario_count": len(packet["valuation_ranges"]),
                "top_review_prompt": packet["review_prompts"][0],
            }
        )
    return {
        "schema_version": "valuation-scenario-lab.demo-gallery.v0.5",
        "generated_on": "static-local",
        "company_count": len(cards),
        "cards": cards,
        "gallery_note": "Neutral bundled fixtures for deterministic command demonstrations.",
        "boundaries": BOUNDARIES,
    }
