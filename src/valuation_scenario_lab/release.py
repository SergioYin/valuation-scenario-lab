from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .doctor import fixture_doctor

PRIVATE_TERMS = [
    "Her" + "mes",
    "Fei" + "shu",
    "/" + "home" + "/" + "xjyin",
    "/" + "mnt" + "/" + "c",
    "tok" + "en=",
]
REQUIRED_FILES = [
    "README.md",
    "pyproject.toml",
    "LICENSE",
    "CHANGELOG.md",
    "RELEASE_NOTES.md",
    "examples/company.json",
    "examples/software-compounder.json",
    "demo/valuation-packet.json",
    "demo/valuation-packet.md",
    "demo/valuation-packet.html",
    "demo/compare-history.json",
    "demo/compare-history.md",
    "demo/review-ledger.json",
    "demo/review-ledger.md",
    "demo/sensitivity-matrix.json",
    "demo/sensitivity-matrix.md",
    "demo/assumption-change-walkthrough.json",
    "demo/assumption-change-walkthrough.md",
    "demo/assumption-change-walkthrough.html",
    "demo/multi-company-demo-gallery.json",
    "demo/multi-company-demo-gallery.md",
    "demo/multi-company-demo-gallery.html",
    "demo/decision-journal.json",
    "demo/decision-journal.md",
    "demo/quickstart-check.json",
    "demo/quickstart-check.md",
    "demo/visual-receipt.json",
    "demo/visual-receipt.md",
    "demo/visual-receipt.html",
    "demo/public-readiness-landing.json",
    "demo/public-readiness-landing.md",
    "demo/public-readiness-landing.html",
    "demo/fixture-doctor.json",
    "demo/fixture-doctor.md",
    "demo/showcase-dashboard.json",
    "demo/showcase-dashboard.svg",
    "demo/showcase-dashboard.md",
    "demo/showcase-dashboard.html",
    "demo/thesis-brief.json",
    "demo/thesis-brief.md",
    "demo/thesis-brief.html",
    "demo/scenario-library.json",
    "demo/scenario-library.md",
    "demo/scenario-library.html",
    "docs/release-checks.md",
    "release/release-manifest.json",
    "release/release-manifest.md",
    "skills/agent/valuation-scenario-lab/SKILL.md",
]


def validate_release(root: Path) -> dict[str, Any]:
    findings = []
    for name in REQUIRED_FILES:
        if not (root / name).exists():
            findings.append({"severity": "error", "message": f"missing {name}"})
    if (root / ".github" / "workflows").exists():
        findings.append({"severity": "error", "message": "GitHub workflows are intentionally out of scope"})
    for path in public_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for term in PRIVATE_TERMS:
            if term in text:
                findings.append({"severity": "error", "message": f"private term found in {path.relative_to(root)}"})
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    for phrase in ["No live data", "No broker", "No buy/sell/hold advice", "valuation-scenario-lab selfcheck"]:
        if phrase not in readme:
            findings.append({"severity": "warning", "message": f"README missing phrase: {phrase}"})
    if (root / "examples").exists():
        policy = {}
        if (root / "examples" / "review-policy.json").exists():
            import json

            policy = json.loads((root / "examples" / "review-policy.json").read_text(encoding="utf-8"))
        doctor = fixture_doctor(root / "examples", policy)
        for item in doctor["issues"]:
            findings.append(
                {
                    "severity": item["severity"],
                    "message": f"fixture-doctor {item['category']} {item['file']} {item['path']}: {item['message']}",
                }
            )
    status = "pass" if not any(item["severity"] == "error" for item in findings) else "fail"
    return {"schema_version": "valuation-scenario-lab.release-validation.v0.7", "status": status, "findings": findings}


def maturity_report(root: Path) -> dict[str, Any]:
    validation = validate_release(root)
    score = 100
    score -= 25 * sum(1 for item in validation["findings"] if item["severity"] == "error")
    score -= 5 * sum(1 for item in validation["findings"] if item["severity"] == "warning")
    return {
        "schema_version": "valuation-scenario-lab.maturity.v0.7",
        "score": max(score, 0),
        "status": "ready" if validation["status"] == "pass" and score >= 90 else "needs work",
        "release_validation": validation,
        "boundaries_checked": True,
    }


def release_manifest(root: Path) -> dict[str, Any]:
    files = []
    for path in public_files(root):
        rel = path.relative_to(root).as_posix()
        files.append({"path": rel, "sha256": sha256(path), "bytes": path.stat().st_size})
    return {"schema_version": "valuation-scenario-lab.release-manifest.v0.7", "files": files}


def public_files(root: Path) -> list[Path]:
    skip_parts = {".git", ".pytest_cache", "__pycache__", ".venv", "dist", "build"}
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.relative_to(root).as_posix() not in {"release/release-manifest.json", "release/release-manifest.md"}
        and not any(part in skip_parts or part.endswith(".egg-info") for part in path.parts)
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()
