"""Fail unless the version in pyproject.toml is higher than the version at a base revision.

Run from the repository root, passing the base revision (e.g. the PR's base commit):
uv run --locked python .github/scripts/check_version.py origin/main
"""

import subprocess
import sys
import tomllib

from packaging.version import Version


def read_version(pyproject):
    return Version(tomllib.loads(pyproject)["project"]["version"])


base_revision = sys.argv[1]
with open("pyproject.toml", encoding="utf-8") as f:
    version = read_version(f.read())
base_pyproject = subprocess.run(
    ["git", "show", f"{base_revision}:pyproject.toml"],
    capture_output=True,
    text=True,
    check=True,
)
base_version = read_version(base_pyproject.stdout)

if version <= base_version:
    # ::error is a GitHub Actions workflow command; it annotates the file in the PR.
    print(
        f"::error file=pyproject.toml::Version {version} must be higher than {base_version} on the base branch. Bump the version in pyproject.toml."
    )
    sys.exit(1)
print(f"Version bumped: {base_version} -> {version}")
