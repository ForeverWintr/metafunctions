To develop metafunctions, install [uv](https://docs.astral.sh/uv/), then create the virtual environment and install the project and its dev dependencies:

    $ uv sync

To run the tests (written in unittest style, run with pytest):

    $ uv run pytest

To run the tests against a specific python version (uv will download it if needed):

    $ uv run --python 3.11 pytest

To release, bump the version and merge to `main`. Bump it with uv, which updates both `pyproject.toml` and `uv.lock` (CI checks that the lockfile is up to date):

    $ uv version --bump patch    # or minor / major, or `uv version <version>` to set it exactly

`.github/workflows/release-pr.yml` keeps a PR from `dev` into `main` open whenever `dev` has unreleased changes, listing the PRs it would release. GitHub Actions opens it, so the checks GitHub starts when it's opened wait for approval: click "Approve workflows to run" on the PR. After a release, `main` has a merge commit `dev` lacks; merge a PR from `main` into `dev` so the next release PR is up to date.

Every PR into `main` must bump the version (enforced by `.github/workflows/version-check.yml`). On each push to `main`, `.github/workflows/release.yml` runs the tests, builds, publishes to PyPI, and creates a GitHub Release (which creates tag `v<version>`).
