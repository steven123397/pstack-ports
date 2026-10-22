"""Check that a ported skill pack's internal references and frontmatter resolve.

Read-only. Exits 1 when a check fails, unless the failure matches --allow.
"""

import argparse
import os
import re

ALLOWED_KEYS = {"name", "description", "globs", "disable-model-invocation", "argument-hint"}
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
BACKTICK = re.compile(r"`((?:\.\./)?(?:references|scripts|playbooks|assets)/[A-Za-z0-9_./-]+)`")
CROSS_SKILL = re.compile(r"\.\./([a-z0-9-]+)/SKILL\.md")
SKILL_URI = re.compile(r"skill://([a-z0-9-]+)(?:/([A-Za-z0-9_./-]+))?")


def markdown_files(root):
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules"}]
        for name in names:
            if name.endswith(".md"):
                yield os.path.join(base, name)


def read(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True)
    parser.add_argument("--allow", action="append", default=[], help="substring allowed to stay unresolved")
    args = parser.parse_args()

    skills_dir = os.path.join(args.port, "skills")
    skills = sorted(
        name for name in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, name))
    )

    problems = []
    allowed = [0]
    links = paths = refs = 0

    def record(message):
        if any(token in message for token in args.allow):
            allowed[0] += 1
            return
        problems.append(message)

    for path in markdown_files(args.port):
        rel = os.path.relpath(path, args.port).replace("\\", "/")
        text = read(path)
        base = os.path.dirname(path)

        for match in LINK.finditer(text):
            target = match.group(1).strip()
            if target.startswith(("http", "#", "mailto:")):
                continue
            target = target.split("#")[0]
            if not target:
                continue
            links += 1
            if not os.path.exists(os.path.normpath(os.path.join(base, target))):
                record(f"{rel}: link does not resolve: {target}")

        for match in BACKTICK.finditer(text):
            target = match.group(1)
            if "*" in target:
                continue
            paths += 1
            candidates = [
                os.path.join(base, target),
                os.path.join(os.path.dirname(base), target),
                os.path.join(args.port, target),
            ]
            if not any(os.path.exists(os.path.normpath(candidate)) for candidate in candidates):
                record(f"{rel}: path does not resolve: {target}")

        for match in CROSS_SKILL.finditer(text):
            refs += 1
            if match.group(1) not in skills:
                record(f"{rel}: cross-skill reference to missing skill: {match.group(1)}")

        for match in SKILL_URI.finditer(text):
            refs += 1
            name, sub = match.group(1), match.group(2)
            if name not in skills:
                record(f"{rel}: skill:// to missing skill: {name}")
            elif sub and not os.path.exists(os.path.join(skills_dir, name, sub)):
                record(f"{rel}: skill:// path does not resolve: {name}/{sub}")

    for name in skills:
        path = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.exists(path):
            record(f"skills/{name}: no SKILL.md")
            continue
        text = read(path)
        if not text.startswith("---"):
            record(f"skills/{name}/SKILL.md: no frontmatter")
            continue
        front = text.split("---", 2)[1]
        keys = [
            line.split(":", 1)[0].strip()
            for line in front.splitlines()
            if line and not line.startswith((" ", "\t")) and ":" in line
        ]
        for key in keys:
            if key not in ALLOWED_KEYS:
                record(f"skills/{name}/SKILL.md: unknown frontmatter key: {key}")
        declared = re.search(r"^name:\s*(.+)$", front, re.M)
        value = declared.group(1).strip().strip('"') if declared else None
        if value != name:
            record(f"skills/{name}/SKILL.md: frontmatter name is {value!r}")

    print(
        f"skills {len(skills)}  links {links}  paths {paths}  refs {refs}  "
        f"problems {len(problems)}  allowed {allowed[0]}"
    )
    for problem in problems:
        print("  " + problem)
    raise SystemExit(1 if problems else 0)


if __name__ == "__main__":
    main()