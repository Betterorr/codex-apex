#!/usr/bin/env python3
"""Build and fail-closed validate the domain-neutral Agent Lanes + GOAL package."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".py", ".ps1", ".yaml", ".yml", ".txt"}
REQUIRED_FILES = {
    "DEPLOY-PROMPT.md",
    "README.md",
    "README-GOAL-INTEGRATED.md",
    "TEMPLATE-MANIFEST.md",
    "VERSION-HISTORY.md",
    "value-slice.template.json",
    "value-slice-completion.template.json",
    "current-state.template.json",
    "scripts/build_portable_package.py",
    "scripts/product_value_gate.py",
    "scripts/value_delta_gate.py",
    "scripts/value_slice_ledger.py",
    "scripts/evidence_receipt.py",
    "scripts/control_provenance.py",
    "goal-development-base/AGENTS.md",
    "goal-development-base/.agents/skills/project-orchestrator/SKILL.md",
}
MARKER_DETECTION_FILES = {
    "scripts/build_portable_package.py",
    "scripts/check_callback_post_office.py",
    "scripts/deliver_callback.py",
    "scripts/product_value_gate.py",
    "scripts/render_dashboard.py",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def is_nested_skill_duplicate(relative: Path) -> bool:
    parts = relative.as_posix().split("/")
    marker = ["goal-development-base", ".agents", "skills"]
    for index in range(len(parts) - 4):
        if parts[index : index + 3] == marker and parts[index + 3] == parts[index + 4]:
            return True
    return False


def source_files(source: Path) -> list[Path]:
    files: list[Path] = []
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if "__pycache__" in relative.parts or path.suffix.lower() in {".pyc", ".pyo"}:
            continue
        if is_nested_skill_duplicate(relative):
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(source).as_posix())


def validate_portability(source: Path, files: list[Path], forbidden_terms: list[str]) -> list[str]:
    errors: list[str] = []
    relative_names = {path.relative_to(source).as_posix() for path in files}
    missing = sorted(REQUIRED_FILES - relative_names)
    if missing:
        errors.append("missing required files: " + ", ".join(missing))

    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(source).as_posix()
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError as exc:
            errors.append(f"non-UTF-8 text file: {relative}: {exc}")
            continue
        if "\ufffd" in text and relative not in MARKER_DETECTION_FILES:
            errors.append(f"unicode replacement character found: {relative}")
        for line_number, line in enumerate(text.splitlines(), 1):
            if (
                "???" in line
                and relative not in MARKER_DETECTION_FILES
                and "乱码" not in line
                and "GARBLED_MARKERS" not in line
            ):
                errors.append(f"suspicious question-mark corruption: {relative}:{line_number}")
        lowered = text.casefold()
        for term in forbidden_terms:
            match_index = lowered.find(term.casefold())
            if match_index >= 0:
                line_number = text.count("\n", 0, match_index) + 1
                errors.append(f"source-specific term: {relative}:{line_number}: {term}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a domain-neutral Agent Lanes + GOAL release package.")
    parser.add_argument("--source", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output-dir", default="artifacts/template-packages")
    parser.add_argument("--version", default=datetime.now().strftime("%Y%m%d-%H%M%S"))
    parser.add_argument(
        "--forbid-term",
        action="append",
        default=[],
        help="Source-project term that must not appear in the portable package; repeat as needed.",
    )
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output_dir = Path(args.output_dir).resolve()
    files = source_files(source)
    errors = validate_portability(source, files, args.forbid_term)
    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False, indent=2))
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"agent-lanes-goal-integrated-template-{args.version}"
    zip_path = output_dir / f"{stem}.zip"
    manifest_path = output_dir / f"{stem}.manifest.json"
    package_root = "agent-lanes-goal-integrated-template"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(source).as_posix()
            archive.write(path, f"{package_root}/{relative}")

    manifest = {
        "schema_version": "agent-lanes.portable-package-manifest.v1",
        "version": args.version,
        "source": "agent-lanes-goal-integrated-template",
        "package": zip_path.name,
        "sha256": sha256_file(zip_path),
        "file_count": len(files),
        "domain_neutral_scan": "PASS",
        "garbled_text_scan": "PASS",
        "nested_skill_duplicates_included": False,
        "built_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "zip": str(zip_path), "manifest": str(manifest_path), **manifest}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
