'''
Testing tools
'''
import unittest
import tempfile
import sys
import random
import functools
import os
import pathlib
import itertools
import string
from collections import defaultdict
import shutil


class BaseTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self._tempdir = None
        self.seed = random.randrange(sys.maxsize)

    @property
    def self_destructing_directory(self):
        '''Return a temporary directory that exists for the duration of the test and is automatically removed after teardown.
        '''
        if not (self._tempdir and os.path.exists(self._tempdir.name)):
            self._tempdir = tempfile.TemporaryDirectory(prefix='{}_'.format(self._testMethodName))
            self.addCleanup(self.cleanup_self_destructing_directory)
            self._tempdir.__enter__()
        return self._tempdir.name

    def cleanup_self_destructing_directory(self):
        # Only try to exit the temporaryDirectory context manager if the directory still exists
        if os.path.exists(self._tempdir.name):
            self._tempdir.__exit__(None, None, None)

    def _formatMessage(self, msg, standardMsg):
        msg = msg or ''
        return super()._formatMessage(msg=f'{msg} (seed: {self.seed})', standardMsg=standardMsg)


