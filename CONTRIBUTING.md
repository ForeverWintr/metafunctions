To develop metafunctions, install [uv](https://docs.astral.sh/uv/), then create the virtual environment and install the project and its dev dependencies:

    $ uv sync

To run the tests:

    $ uv run python -m unittest discover

To run the tests against a specific python version (uv will download it if needed):

    $ uv run --python 3.9 python -m unittest discover

To build and publish a release:

    $ uv build
    $ uv publish
