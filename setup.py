import os
import contextlib
import pathlib
from setuptools import setup, find_packages

import pandoc

import metafunctions


here = os.path.abspath(os.path.dirname(__file__))

@contextlib.contextmanager
def md_to_rst(dir_):
    '''Convert anything with a .md extension to .rst for the duration of this context manager.
    '''
    dir_ = pathlib.Path(dir_)
    rstfiles = []
    for mdfile in dir_.glob('*.md'):
        doc = pandoc.Document()
        doc.markdown = mdfile.read_bytes()
        rstfile = mdfile.with_suffix('.rst')
        rstfile.write_bytes(doc.rst)
        rstfiles.append(rstfile)

    yield rstfiles
    for f in rstfiles:
        f.unlink()


with md_to_rst(here):
    with open(os.path.join(here, 'README.rst')) as f:
        long_description=f.read()


    setup(
        name=metafunctions.__name__,
        version=metafunctions.__version__,
        description='Metafunctions is a function composition and data pipelining library',
        long_description=long_description,
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
    )
