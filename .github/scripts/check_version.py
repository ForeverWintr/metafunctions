"""Fail unless the version in pyproject.toml is higher than every v* release tag on origin.

Run from the repository root: uv run --locked python .github/scripts/check_version.py
"""

import subprocess
import sys
import tomllib

from packaging.version import Version

with open("pyproject.toml", "rb") as f:
    version = Version(tomllib.load(f)["project"]["version"])

ls_remote = subprocess.run(
    ["git", "ls-remote", "--tags", "--refs", "origin", "refs/tags/v*"],
    capture_output=True,
    text=True,
    check=True,
)
released = [
    Version(line.split()[1].removeprefix("refs/tags/v"))
    for line in ls_remote.stdout.splitlines()
]

latest = max(released, default=Version("0"))
if version <= latest:
    # ::error is a GitHub Actions workflow command; it annotates the file in the PR.
    print(
        f"::error file=pyproject.toml::Version {version} must be higher than the latest release, {latest}. Bump the version in pyproject.toml."
    )
    sys.exit(1)
print(f"Version bumped: {latest} -> {version}")
