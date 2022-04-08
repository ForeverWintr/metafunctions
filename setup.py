"""
MetaFunctions is a function composition and data pipelining library.

For more information, please visit the `project on github <https://github.com/ForeverWintr/metafunctions>`_.
"""

import os
import sys
import contextlib
import pathlib
import shutil
from setuptools import setup, find_packages, Command

import metafunctions

here = os.path.abspath(os.path.dirname(__file__))


class UploadCommand(Command):
    """
    Support setup.py upload.
    https://github.com/kennethreitz/setup.py/blob/master/setup.py
    """

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            shutil.rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPi via Twine…")
        os.system("twine upload dist/*")

        sys.exit()


setup(
    name=metafunctions.__name__,
    version=metafunctions.__version__,
    description="Metafunctions is a function composition and data pipelining library",
    long_description=__doc__,
    url="https://github.com/ForeverWintr/metafunctions",
    author="Tom Rutherford",
    author_email="foreverwintr@gmail.com",
    license="MIT",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="functional-programming function-composition",
    packages=find_packages(),
    test_suite="metafunctions.tests",
    install_requires="ansicolors>=1.1.8",
    # $ setup.py publish support.
    cmdclass={
        "upload": UploadCommand,
    },
)
