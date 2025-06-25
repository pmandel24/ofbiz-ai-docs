#!/usr/bin/env python3
"""Generate a project-manifest.yaml containing a list of all files with basic metadata.
The manifest is written at repo root. Intended to be run in CI or locally.
"""
from __future__ import annotations
import datetime as _dt
import json as _json
import os as _os
from pathlib import Path
import subprocess as _sp
import sys

try:
    import yaml  # type: ignore
except ModuleNotFoundError:
    yaml = None  # Will fall back to JSON if YAML not available

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_FILE = REPO_ROOT / "project-manifest.yaml"

# Collect file metadata
files: list[dict[str, object]] = []
for path in REPO_ROOT.rglob("*"):
    if path.is_file() and ".git" not in path.parts and path.name != MANIFEST_FILE.name:
        rel_path = path.relative_to(REPO_ROOT)
        try:
            line_count = sum(1 for _ in path.open("rb"))
        except Exception:
            line_count = None
        files.append(
            {
                "path": str(rel_path),
                "size": path.stat().st_size,
                "lines": line_count,
            }
        )

manifest: dict[str, object] = {
    "generated_at": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "git_revision": _sp.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT).decode().strip(),
    "file_count": len(files),
    "files": sorted(files, key=lambda f: f["path"]),
}

if yaml:
    MANIFEST_FILE.write_text(yaml.safe_dump(manifest, sort_keys=False))
else:
    # Fallback to JSON if PyYAML isn't available
    MANIFEST_FILE.write_text(_json.dumps(manifest, indent=2))

print(f"project-manifest.yaml generated with {manifest['file_count']} entries → {MANIFEST_FILE}")
