from metafunctions import decorators
from metafunctions.core import SimpleFunction
from metafunctions.core import MetaFunction
from metafunctions.tests.util import BaseTestCase


class TestUnit(BaseTestCase):
    def test_node_bind(self):
        '''Node bind rules:
        The MetaFunction recieved in a base function when bind is true is the
        function that was called. E.g., if a SimpleFunction is called directly, meta will be that
        SimpleFunction itself. However, if the SimpleFunction is contained within a hierarchy of
        other MetaFunction, meta will be the highest level (i.e., outermost) Metafunction.
        '''
        @decorators.node(bind=True)
        def a(meta, x):
            self.assertIsInstance(meta, MetaFunction)
            meta.data['a'] = 'b'
            return x + 'a'
        @decorators.node(bind=True)
        def f(meta, x):
            return x + meta.data.get('a', 'f')

        self.assertEqual(a('_'), '_a')
        self.assertEqual(f('_'), '_f')

        cmp = a | f
        self.assertEqual(cmp('_'), '_ab')
        cmp = f | a | a | f + f
        self.assertEqual(cmp('_'), '_faab_faab')

    def test_node_bracketless(self):
        '''I'm allowing the node decorator to be applied without calling because this is how both
        celery and function_pipes work.
        '''
        @decorators.node
        def a(x):
            return x + 'a'
        @decorators.node()
        def b(x):
            return x + 'b'

        self.assertIsInstance(a, SimpleFunction)
        self.assertIsInstance(b, SimpleFunction)
        self.assertEqual((b|a)('_'), '_ba')
