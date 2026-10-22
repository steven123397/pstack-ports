"""Compare document skeletons between two trees.

The invariant is that no upstream step disappears. Heading numbers are ignored so
renumbering is not a mismatch, added headings are reported as additions, and any
upstream heading or numbered item that the port lacks is a failure. Read-only.
"""

import argparse
import os
import re

HEADING = re.compile(r"^(#{2,4})\s*(.+)$")
NUMBERED = re.compile(r"^(?:\d+\.|[-*]\s\*\*|###?\s*\d)")
STEP_PREFIX = re.compile(r"^\d+[a-z]?\.\s*")


def walk(root):
    files = set()
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules"}]
        for name in names:
            if name.endswith(".md"):
                files.add(os.path.relpath(os.path.join(base, name), root).replace("\\", "/"))
    return files


def outline(path):
    headings, numbered = [], 0
    with open(path, encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            match = HEADING.match(line)
            if match:
                headings.append(STEP_PREFIX.sub("", match.group(2)).strip())
            elif NUMBERED.match(line):
                numbered += 1
    return headings, numbered


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--subdir", default="skills")
    parser.add_argument("--ignore", action="append", default=[], help="substring skipped as a known rename or drop")
    args = parser.parse_args()

    prefix = args.subdir.strip("/") + "/"
    up_files = {rel for rel in walk(args.upstream) if rel.startswith(prefix)}
    port_files = {rel for rel in walk(args.port) if rel.startswith(prefix)}
    skipped = {rel for rel in up_files | port_files if any(token in rel for token in args.ignore)}
    up_files -= skipped
    port_files -= skipped

    failures = 0
    additions = 0
    compared = 0
    for rel in sorted(up_files & port_files):
        up_heads, up_steps = outline(os.path.join(args.upstream, rel))
        port_heads, port_steps = outline(os.path.join(args.port, rel))
        compared += 1
        if len(port_heads) < len(up_heads) or port_steps < up_steps:
            failures += 1
            print(
                f"{rel}: structure shrank, headings {len(up_heads)} -> {len(port_heads)}, "
                f"numbered items {up_steps} -> {port_steps}"
            )
            for heading in up_heads:
                if heading not in port_heads:
                    print(f"  upstream heading not found verbatim: {heading[:100]}")
        elif len(port_heads) > len(up_heads) or port_steps > up_steps:
            additions += 1
            print(
                f"{rel}: structure grew, headings {len(up_heads)} -> {len(port_heads)}, "
                f"numbered items {up_steps} -> {port_steps}"
            )

    for rel in sorted(up_files - port_files):
        failures += 1
        print(f"{rel}: missing in port")

    print(f"compared {compared} files, failures {failures}, files with additions {additions}, skipped {len(skipped)}")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()