#!/usr/bin/env bash
# _generate_index.sh — regenerates tickets/README.md from the frontmatter of tickets/*.md.
# Safe to run repeatedly and from concurrent sessions: README.md is a derived artifact,
# never the source of truth (each ticket file's own `status` field is).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

python3 - "$@" <<'PYEOF'
import glob, re, sys

def parse_frontmatter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.split("#", 1)[0].strip()  # strip trailing inline comments
        value = value.strip('"').strip("'")
        fm[key] = value
    return fm

files = sorted(
    f for f in glob.glob("*.md")
    if f != "README.md" and not f.startswith("_")
)

buckets = {
    "blocked": [], "backlog": [], "in-progress": [],
    "in-review": [], "testing": [], "done": [],
}

for path in files:
    fm = parse_frontmatter(path)
    status = fm.get("status", "backlog")
    title = fm.get("title", path)
    ticket_id = fm.get("id", "?")
    role = fm.get("assigned-role", "unassigned")
    line = f"- **{ticket_id}** [{title}]({path}) — {role}"
    buckets.get(status, buckets["backlog"]).append(line)

out = ["# Tickets\n"]
out.append(
    "This file is **generated** by `_generate_index.sh` — do not hand-edit it. "
    "Status lives in each ticket's own frontmatter; this is a derived view.\n"
)

section_titles = [
    ("blocked", "Blocked"),
    ("backlog", "Backlog"),
    ("in-progress", "In Progress"),
    ("in-review", "In Review"),
    ("testing", "Testing"),
    ("done", "Done"),
]

for key, label in section_titles:
    items = buckets[key]
    out.append(f"## {label} ({len(items)})\n")
    if not items:
        out.append("_none_\n")
    else:
        if key == "done":
            items = items[-10:]  # keep the index short; full history lives in git log
        out.extend(items)
        out.append("")

with open("README.md", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

print(f"Regenerated README.md from {len(files)} ticket file(s).")
PYEOF
