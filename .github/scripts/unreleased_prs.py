"""Print a Markdown list of PRs merged into dev whose changes aren't on main yet.

Used as the description of the dev -> main release PR. Run from the repository root with
origin/main fetched and gh authenticated:
python .github/scripts/unreleased_prs.py
"""

import json
import subprocess

# Unreleased PRs are the most recent ones, so this only needs to cover what's merged between releases.
merged_prs = subprocess.run(
    [
        "gh",
        "pr",
        "list",
        "--base",
        "dev",
        "--state",
        "merged",
        "--limit",
        "100",
        "--json",
        "number,title,mergeCommit",
    ],
    capture_output=True,
    text=True,
    check=True,
)

for pr in json.loads(merged_prs.stdout):
    # Exit code 0 means the merge commit is on main, 1 means it isn't; anything else is an error.
    on_main = subprocess.run(
        ["git", "merge-base", "--is-ancestor", pr["mergeCommit"]["oid"], "origin/main"],
        check=False,
    )
    if on_main.returncode == 1:
        print(f"- #{pr['number']} {pr['title']}")
    elif on_main.returncode != 0:
        on_main.check_returncode()
