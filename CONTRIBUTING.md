To develop metafunctions, install [uv](https://docs.astral.sh/uv/), then create the virtual environment and install the project and its dev dependencies:

    $ uv sync

To run the tests (written in unittest style, run with pytest):

    $ uv run pytest

To run the tests against a specific python version (uv will download it if needed):

    $ uv run --python 3.11 pytest

To release, bump `version` in `pyproject.toml` and merge to `main`. Every PR into `main` must bump the version (enforced by `.github/workflows/version-check.yml`). On each push to `main`, `.github/workflows/release.yml` checks whether tag `v<version>` exists. If it doesn't, the workflow runs the tests, builds, publishes to PyPI, and creates a GitHub Release (which creates the tag).

To build and publish manually, as a fallback:

    $ uv build
    $ uv publish
