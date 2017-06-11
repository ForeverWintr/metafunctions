
from setuptools import setup, find_packages

import metafunctions

setup(
    name=metafunctions.__name__,
    version=metafunctions.__version__,
    description='Metafunctions is a function composition and data pipelining library',
    url='https://github.com/ForeverWintr/metafunctions',
    author='Tom Rutherford',
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
)
