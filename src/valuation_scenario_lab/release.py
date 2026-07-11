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
    "demo/reproducibility-audit.json",
    "demo/reproducibility-audit.md",
    "demo/reproducibility-audit.html",
    "demo/sample-workflow.json",
    "demo/sample-workflow.md",
    "demo/sample-workflow.html",
    "demo/casebook.json",
    "demo/casebook.md",
    "demo/casebook.html",
    "demo/onboarding-template/README.md",
    "demo/onboarding-template/company.json",
    "demo/onboarding-template/review-policy.json",
    "demo/onboarding-template/prior-packet.json",
    "docs/release-checks.md",
    "release/release-manifest.json",
    "release/release-manifest.md",
    "skills/agent/valuation-scenario-lab/SKILL.md",
]

EXPECTED_SCHEMA_VERSIONS = {
    "demo/valuation-packet.json": "valuation-scenario-lab.v0.5",
    "demo/compare-history.json": "valuation-scenario-lab.compare.v0.5",
    "demo/review-ledger.json": "valuation-scenario-lab.ledger.v0.5",
    "demo/sensitivity-matrix.json": "valuation-scenario-lab.sensitivity.v0.5",
    "demo/assumption-change-walkthrough.json": "valuation-scenario-lab.assumption-change.v0.5",
    "demo/multi-company-demo-gallery.json": "valuation-scenario-lab.demo-gallery.v0.5",
    "demo/decision-journal.json": "valuation-scenario-lab.decision-journal.v0.5",
    "demo/quickstart-check.json": "valuation-scenario-lab.quickstart-check.v0.5",
    "demo/visual-receipt.json": "valuation-scenario-lab.visual-receipt.v0.5",
    "demo/fixture-doctor.json": "valuation-scenario-lab.fixture-doctor.v0.5",
    "demo/public-readiness-landing.json": "valuation-scenario-lab.public-readiness.v0.5",
    "demo/showcase-dashboard.json": "valuation-scenario-lab.showcase-dashboard.v0.6",
    "demo/thesis-brief.json": "valuation-scenario-lab.thesis-brief.v0.7",
    "demo/scenario-library.json": "valuation-scenario-lab.scenario-library.v0.7",
    "demo/reproducibility-audit.json": "valuation-scenario-lab.reproducibility-audit.v0.8",
    "demo/sample-workflow.json": "valuation-scenario-lab.sample-workflow.v0.8",
    "demo/casebook.json": "valuation-scenario-lab.casebook.v0.9",
}

SAFETY_BOUNDARIES = [
    "No live data.",
    "No broker connections.",
    "No buy/sell/hold advice.",
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
    deps = dependency_metadata_checks(root)
    if deps["status"] != "pass":
        for item in deps["checks"]:
            if not item["ok"]:
                findings.append({"severity": "error", "message": f"dependency metadata check failed: {item['name']}"})
    manifest = manifest_coverage_checks(root)
    if manifest["status"] != "pass":
        if manifest["missing"]:
            findings.append({"severity": "error", "message": f"release manifest missing {len(manifest['missing'])} public files"})
        if manifest["extra"]:
            findings.append({"severity": "error", "message": f"release manifest has {len(manifest['extra'])} extra files"})
        if manifest["hash_mismatches"]:
            findings.append({"severity": "error", "message": f"release manifest has {len(manifest['hash_mismatches'])} hash mismatches"})
    boundaries = safety_boundary_checks(root)
    if boundaries["status"] != "pass":
        for name in boundaries["files_missing_boundaries"]:
            findings.append({"severity": "error", "message": f"safety boundaries missing in {name}"})
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
    return {"schema_version": "valuation-scenario-lab.release-validation.v0.8", "status": status, "findings": findings}


def maturity_report(root: Path) -> dict[str, Any]:
    validation = validate_release(root)
    score = 100
    score -= 25 * sum(1 for item in validation["findings"] if item["severity"] == "error")
    score -= 5 * sum(1 for item in validation["findings"] if item["severity"] == "warning")
    return {
        "schema_version": "valuation-scenario-lab.maturity.v0.8",
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
    return {"schema_version": "valuation-scenario-lab.release-manifest.v0.8", "files": files}


def reproducibility_audit(root: Path, generated_outputs: list[str] | None = None) -> dict[str, Any]:
    generated = set(generated_outputs or [])
    artifact_presence = artifact_presence_checks(root, generated)
    schema_versions = schema_version_checks(root, generated)
    manifest_coverage = manifest_coverage_checks(root)
    dependency_metadata = dependency_metadata_checks(root)
    safety_boundaries = safety_boundary_checks(root)
    sections = [
        artifact_presence,
        schema_versions,
        manifest_coverage,
        dependency_metadata,
        safety_boundaries,
    ]
    status = "pass" if all(section["status"] == "pass" for section in sections) else "fail"
    return {
        "schema_version": "valuation-scenario-lab.reproducibility-audit.v0.8",
        "status": status,
        "generated_on": "static-local",
        "checks": {
            "artifact_presence": artifact_presence,
            "schema_versions": schema_versions,
            "hash_manifest_coverage": manifest_coverage,
            "zero_dependency_metadata": dependency_metadata,
            "safety_boundary_coverage": safety_boundaries,
        },
        "boundaries": SAFETY_BOUNDARIES,
    }


def artifact_presence_checks(root: Path, generated_outputs: set[str]) -> dict[str, Any]:
    items = []
    for name in REQUIRED_FILES:
        exists = (root / name).exists()
        generated_by_command = name in generated_outputs and not exists
        items.append({"path": name, "exists": exists, "generated_by_command": generated_by_command})
    missing = [item["path"] for item in items if not item["exists"] and not item["generated_by_command"]]
    return {"status": "pass" if not missing else "fail", "missing": missing, "files": items}


def schema_version_checks(root: Path, generated_outputs: set[str] | None = None) -> dict[str, Any]:
    import json

    generated = generated_outputs or set()
    items = []
    for name, expected in EXPECTED_SCHEMA_VERSIONS.items():
        path = root / name
        actual = None
        valid_json = False
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                valid_json = isinstance(data, dict)
                actual = data.get("schema_version") if isinstance(data, dict) else None
            except json.JSONDecodeError:
                valid_json = False
        generated_by_command = name in generated and not path.exists()
        ok = generated_by_command or (valid_json and actual == expected)
        items.append({"path": name, "expected": expected, "actual": actual, "ok": ok, "generated_by_command": generated_by_command})
    bad = [item["path"] for item in items if not item["ok"]]
    return {"status": "pass" if not bad else "fail", "mismatches": bad, "files": items}


def manifest_coverage_checks(root: Path) -> dict[str, Any]:
    import json

    manifest_path = root / "release" / "release-manifest.json"
    expected = {path.relative_to(root).as_posix(): sha256(path) for path in public_files(root)}
    actual: dict[str, str] = {}
    manifest_schema = None
    if manifest_path.exists():
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_schema = payload.get("schema_version")
            actual = {item.get("path", ""): item.get("sha256", "") for item in payload.get("files", [])}
        except json.JSONDecodeError:
            actual = {}
    missing = sorted(path for path in expected if path not in actual)
    extra = sorted(path for path in actual if path not in expected)
    hash_mismatches = sorted(path for path, digest in expected.items() if path in actual and actual[path] != digest)
    ok = manifest_path.exists() and not missing and not extra and not hash_mismatches
    return {
        "status": "pass" if ok else "fail",
        "manifest_schema_version": manifest_schema,
        "expected_file_count": len(expected),
        "manifest_file_count": len(actual),
        "missing": missing,
        "extra": extra,
        "hash_mismatches": hash_mismatches,
    }


def dependency_metadata_checks(root: Path) -> dict[str, Any]:
    pyproject = root / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8") if pyproject.exists() else ""
    checks = [
        {"name": "pyproject_exists", "ok": pyproject.exists()},
        {"name": "dependencies_empty", "ok": "dependencies = []" in text},
        {"name": "no_install_requires", "ok": "install_requires" not in text},
        {"name": "no_requirements_txt", "ok": not (root / "requirements.txt").exists()},
        {"name": "no_runtime_dependency_group", "ok": "[project.optional-dependencies]" not in text},
    ]
    return {"status": "pass" if all(item["ok"] for item in checks) else "fail", "checks": checks}


def safety_boundary_checks(root: Path) -> dict[str, Any]:
    text_files = [
        "README.md",
        "demo/valuation-packet.md",
        "demo/valuation-packet.html",
        "demo/public-readiness-landing.md",
        "demo/public-readiness-landing.html",
        "demo/quickstart-check.md",
        "demo/visual-receipt.md",
        "demo/visual-receipt.html",
        "demo/showcase-dashboard.md",
        "demo/showcase-dashboard.svg",
        "demo/showcase-dashboard.html",
        "demo/thesis-brief.md",
        "demo/thesis-brief.html",
        "demo/scenario-library.md",
        "demo/scenario-library.html",
        "demo/casebook.md",
        "demo/casebook.html",
        "demo/onboarding-template/README.md",
        "skills/agent/valuation-scenario-lab/SKILL.md",
    ]
    files = []
    for name in text_files:
        path = root / name
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        present = [boundary for boundary in SAFETY_BOUNDARIES if boundary in text]
        files.append({"path": name, "exists": path.exists(), "present": present, "missing": [b for b in SAFETY_BOUNDARIES if b not in present]})
    bad = [item["path"] for item in files if not item["exists"] or item["missing"]]
    return {"status": "pass" if not bad else "fail", "files_missing_boundaries": bad, "files": files}


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
