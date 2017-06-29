import os
import contextlib
import pathlib
import shutil
from setuptools import setup, find_packages

import metafunctions

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name=metafunctions.__name__,
    version=metafunctions.__version__,
    description='Metafunctions is a function composition and data pipelining library',
    #long_description=long_description,
    url='https://github.com/ForeverWintr/metafunctions',
    author='Tom Rutherford',
    author_email='tom.rutherford@alumni.uleth.ca',
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='functional-programming function-composition',
    packages=find_packages(),
    test_suite='metafunctions.tests',
    install_requires=requirements
)
