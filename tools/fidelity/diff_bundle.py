"""Pair two trees by relative path and write one unified diff per changed file.

Read-only. Prints a summary and writes MANIFEST.tsv plus <file>.diff files.
Binary files are counted, never diffed.
"""

import argparse
import difflib
import os
import shutil

SKIP_DIRS = {".git", "node_modules", "dist"}
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_UPSTREAM = os.path.join(REPO_ROOT, ".upstream", "cursor-plugins", "pstack")


def walk(root):
    files = set()
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in names:
            files.add(os.path.relpath(os.path.join(base, name), root).replace("\\", "/"))
    return files


def read_lines(path):
    with open(path, "rb") as handle:
        raw = handle.read()
    if b"\x00" in raw:
        return None
    return raw.decode("utf-8", errors="replace").splitlines()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", default=DEFAULT_UPSTREAM, help="upstream pstack tree (default: %(default)s)")
    parser.add_argument("--port", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--subdir", default="", help="restrict to one subtree, for example skills")
    parser.add_argument("--context", type=int, default=3)
    args = parser.parse_args()
    if not os.path.isdir(args.upstream):
        raise SystemExit(f"upstream not found: {args.upstream}\nrun: node tools/upstream/sync.mjs")

    up_files, port_files = walk(args.upstream), walk(args.port)
    if args.subdir:
        prefix = args.subdir.strip("/") + "/"
        up_files = {rel for rel in up_files if rel.startswith(prefix)}
        port_files = {rel for rel in port_files if rel.startswith(prefix)}

    shutil.rmtree(args.out, ignore_errors=True)
    os.makedirs(args.out, exist_ok=True)

    rows = []
    for rel in sorted(up_files | port_files):
        in_up, in_port = rel in up_files, rel in port_files
        a = read_lines(os.path.join(args.upstream, rel)) if in_up else None
        b = read_lines(os.path.join(args.port, rel)) if in_port else None
        if (in_up and a is None) or (in_port and b is None) or not (in_up and in_port):
            status = "NEW" if not in_up else "GONE" if not in_port else "BINARY"
            if status == "BINARY" and a is None and b is None:
                rows.append((rel, status, 0, 0))
            else:
                rows.append((rel, status, len(b or a or []), len(b or a or [])))
            continue
        diff = list(
            difflib.unified_diff(
                a, b, fromfile="upstream/" + rel, tofile="port/" + rel, lineterm="", n=args.context
            )
        )
        if not diff:
            rows.append((rel, "SAME", len(a), 0))
            continue
        changed = sum(
            1
            for line in diff
            if (line.startswith("+") or line.startswith("-")) and not line.startswith(("+++", "---"))
        )
        with open(os.path.join(args.out, rel.replace("/", "__") + ".diff"), "w", encoding="utf-8") as handle:
            handle.write("\n".join(diff) + "\n")
        rows.append((rel, "DIFF", len(a), changed))

    with open(os.path.join(args.out, "MANIFEST.tsv"), "w", encoding="utf-8") as handle:
        handle.write("file\tstatus\tup_lines\tchanged_lines\n")
        for row in rows:
            handle.write("\t".join(str(cell) for cell in row) + "\n")

    counts = {
        status: sum(1 for row in rows if row[1] == status)
        for status in ("SAME", "DIFF", "NEW", "GONE", "BINARY")
    }
    changed_total = sum(row[3] for row in rows if row[1] == "DIFF")
    up_total = sum(row[2] for row in rows if row[1] in ("SAME", "DIFF", "GONE"))
    print(f"files {len(rows)}  " + "  ".join(f"{key.lower()} {value}" for key, value in counts.items()))
    if up_total:
        print(f"changed lines {changed_total} of {up_total} upstream lines ({changed_total / up_total:.1%})")
    print(f"bundle {args.out}")
    print("\nlargest diffs:")
    for rel, status, _, changed in sorted(rows, key=lambda row: -row[3])[:10]:
        if changed:
            print(f"  {changed:5d} {status:4s} {rel}")


if __name__ == "__main__":
    main()