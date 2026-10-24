#!/usr/bin/env python3
"""Spawn pstack agents and compare their resolved model with the configured role.

Usage:
  python probe_routing.py [agent] [--all] [--max-time SECONDS] [--json-out PATH]

Exits 0 only when every probed agent completed and its resolvedModel equals the
value of that agent's modelRole in `omp config get modelRoles`.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# agent -> model role pinned by its frontmatter in pstack-omp/agents/
AGENT_ROLES = {
    "pstack-worker": "pstack-fast",
    "pstack-reader": "pstack-fast",
    "pstack-judge": "pstack-judge",
    "pstack-panel": "pstack-panel",
}


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    exe = shutil.which(args[0])
    if exe is None:
        raise SystemExit(f"{args[0]}: not found on PATH")
    argv = [exe, *args[1:]]
    if os.name == "nt" and exe.lower().endswith((".cmd", ".bat")):
        argv = ["cmd", "/c", *argv]
    return subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace")


def configured_roles() -> dict[str, str]:
    proc = run(["omp", "config", "get", "modelRoles"])
    if proc.returncode != 0:
        raise SystemExit(f"omp config get modelRoles exited {proc.returncode}: {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def walk(node, hits: list[dict]) -> None:
    if isinstance(node, dict):
        if "resolvedModel" in node and "modelRole" in node:
            hits.append(node)
        for value in node.values():
            walk(value, hits)
    elif isinstance(node, list):
        for value in node:
            walk(value, hits)


def saw_output(node) -> bool:
    if isinstance(node, dict):
        if node.get("recentOutput") == ["OK"]:
            return True
        return any(saw_output(value) for value in node.values())
    if isinstance(node, list):
        return any(saw_output(value) for value in node)
    return False


def probe(agent: str, max_time: str) -> tuple[dict | None, str, bool]:
    prompt = (
        "Call the task tool exactly once with this exact argument object and no other tools: "
        '{"context":"trivial","tasks":[{"task":"Reply with exactly OK",'
        f'"solutionSpace":"trivial","agent":"{agent}"}}],"i":"Probing agent routing"}}. '
        "Then call the wait tool so the task result is delivered, and reply DONE only after the "
        "task reports completed."
    )
    proc = run(["omp", "-p", "--mode", "json", "--auto-approve", "--max-time", max_time, prompt])
    hits: list[dict] = []
    output_ok = False
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        walk(event, hits)
        output_ok = output_ok or saw_output(event)
    completed = [hit for hit in hits if hit.get("status") == "completed"]
    last = (completed or hits or [None])[-1]
    return last, proc.stdout, output_ok


def report(agent: str, roles: dict[str, str], max_time: str) -> tuple[bool, str, str]:
    role = AGENT_ROLES[agent]
    hit, raw, output_ok = probe(agent, max_time)
    expected = roles.get(role)
    if hit is None:
        return False, (
            f"{agent}: no resolvedModel in the stream. The agent may not be registered; "
            "check `omp plugin doctor` and that omp plugin list --json shows pstack-omp enabled."
        ), raw
    resolved = hit.get("resolvedModel")
    status = hit.get("status")
    rows = [
        f"agent        : {agent}",
        f"model role   : {hit.get('modelRole')}",
        f"resolved     : {resolved}",
        f"configured   : {expected}",
        f"status       : {status}",
        f"subagent out : {'OK' if output_ok else 'missing'}",
        f"match        : {'yes' if resolved == expected else 'no'}",
    ]
    ok = resolved == expected and status == "completed" and output_ok
    return ok, "\n".join(rows), raw


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("agent", nargs="?", default="pstack-reader", choices=sorted(AGENT_ROLES))
    parser.add_argument("--all", action="store_true", help="probe all four pstack agents")
    parser.add_argument("--max-time", default="300", help="per-run cap in seconds (omp --max-time)")
    parser.add_argument("--json-out", help="write the raw JSON stream for the last run here")
    args = parser.parse_args()

    roles = configured_roles()
    agents = sorted(AGENT_ROLES) if args.all else [args.agent]
    failures = 0
    for agent in agents:
        ok, summary, raw = report(agent, roles, args.max_time)
        print(summary + "\n")
        failures += 0 if ok else 1
        if args.json_out:
            out = Path(args.json_out)
            if len(agents) > 1:
                out = out.with_name(f"{out.stem}-{agent}{out.suffix}")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(raw, encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())