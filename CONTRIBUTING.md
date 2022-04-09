To develop metafunctions, first create a virtual environment, then install the project in development mode:

    $ python3 -m venv venv
    $ . venv/bin/activate
    $ pip install -e .

Then install extra dev requirements:

    $ pip install -r requirements-dev.txt

The project uses Tox to run tests against multiple python versions. To run the tests:

    $ tox
