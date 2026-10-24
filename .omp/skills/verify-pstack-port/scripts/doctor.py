#!/usr/bin/env python3
"""Read-only readiness check for the pstack-omp install that omp resolves.

Prints one line per check and exits 1 if any check fails. Spends no model tokens.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
PLUGIN_DIR = REPO / "pstack-omp"
ROLE_KEYS = ("pstack-fast", "pstack-judge", "pstack-panel")


def run(args: list[str]) -> tuple[int, str, str]:
    exe = shutil.which(args[0])
    if exe is None:
        return 127, "", f"{args[0]}: not found on PATH"
    argv = [exe, *args[1:]]
    if os.name == "nt" and exe.lower().endswith((".cmd", ".bat")):
        argv = ["cmd", "/c", *argv]
    proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout, proc.stderr


def check_plugin_dir() -> tuple[bool, str]:
    code, out, err = run(["omp", "plugin", "list", "--json"])
    if code != 0:
        return False, f"omp plugin list --json exited {code}: {(err or out).strip()[:300]}"
    try:
        data = json.loads(out)
    except json.JSONDecodeError as exc:
        return False, f"plugin list is not JSON: {exc}"
    entries = data.get("npm") or []
    entry = next((item for item in entries if item.get("name") == "pstack-omp"), None)
    if entry is None:
        return False, "pstack-omp is not installed under npm; run omp plugin link ./pstack-omp"
    path = entry.get("path") or ""
    if not entry.get("enabled"):
        return False, f"pstack-omp is installed at {path} but disabled"
    if os.path.realpath(path) != os.path.realpath(PLUGIN_DIR):
        return False, f"install path {path} is not {PLUGIN_DIR}; the checkout is not what omp loads"
    return True, f"pstack-omp enabled at {path}"


def check_doctor() -> tuple[bool, str]:
    code, out, err = run(["omp", "plugin", "doctor"])
    text = out + err
    if code != 0:
        return False, f"omp plugin doctor exited {code}"
    summary = [line.strip() for line in text.splitlines() if line.strip().startswith("Summary:")]
    if not summary:
        return False, "doctor printed no Summary line"
    return ("0 errors" in summary[-1]), summary[-1]


def check_skill_resolution() -> tuple[bool, str]:
    code, out, err = run(["omp", "read", "skill://poteto-mode/SKILL.md:2-3"])
    if code != 0:
        return False, f"skill://poteto-mode/SKILL.md did not resolve: {(err or out).strip()[:300]}"
    if "name: poteto-mode" not in out:
        return False, "poteto-mode resolved but its frontmatter name is missing"
    return True, "skill://poteto-mode/SKILL.md resolves from the plugin"


def check_roles() -> tuple[bool, str]:
    code, out, err = run(["omp", "config", "get", "modelRoles"])
    if code != 0:
        return False, f"omp config get modelRoles exited {code}: {(err or out).strip()[:300]}"
    try:
        roles = json.loads(out)
    except json.JSONDecodeError as exc:
        return False, f"modelRoles is not JSON: {exc}"
    missing = [key for key in ROLE_KEYS if key not in roles]
    if missing:
        return False, f"modelRoles is missing {', '.join(missing)}; those agents inherit the parent model"
    return True, "modelRoles pins " + ", ".join(f"{key}={roles[key]}" for key in ROLE_KEYS)


CHECKS = (
    ("plugin-install", check_plugin_dir),
    ("plugin-doctor", check_doctor),
    ("skill-resolution", check_skill_resolution),
    ("model-roles", check_roles),
)


def main() -> int:
    failures = 0
    for name, check in CHECKS:
        try:
            ok, detail = check()
        except Exception as exc:  # noqa: BLE001 - a doctor reports, it does not crash
            ok, detail = False, f"{type(exc).__name__}: {exc}"
        print(f"{'ok  ' if ok else 'FAIL'} {name}: {detail}")
        failures += 0 if ok else 1
    print(f"\n{len(CHECKS) - failures}/{len(CHECKS)} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())