
from metafunctions.tests.util import BaseTestCase

import metafunctions.function_pipe_compat as fpn

class TestUnit(BaseTestCase):

    def test_string_processing(self):
        # examples from https://function-pipe.readthedocs.io/en/latest/usage_strings.html
        @fpn.pipe_node
        @fpn.pipe_kwarg_bind(fpn.PREDECESSOR_RETURN)
        def a(s):
            return s + 'a'

        self.assertEqual(a(**{fpn.PN_INPUT: '_'}), '_a')
