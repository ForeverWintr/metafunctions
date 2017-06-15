
from metafunctions.tests.util import BaseTestCase
from metafunctions.util import store, recall, node, highlight_current_function
from metafunctions.core import MetaFunction, SimpleFunction

class TestUnit(BaseTestCase):
    def test_node_bind(self):
        '''
        Node bind rules:
        The MetaFunction recieved in a base function when bind is true is the
        function that was called. E.g., if a SimpleFunction is called directly, meta will be that
        SimpleFunction itself. However, if the SimpleFunction is contained within a hierarchy of
        other MetaFunction, meta will be the highest level (i.e., outermost) Metafunction.
        '''
        @node(bind=True)
        def a_(meta, x):
            self.assertIsInstance(meta, MetaFunction)
            meta.data['a'] = 'b'
            return x + 'a'
        @node(bind=True)
        def f(meta, x):
            return x + meta.data.get('a', 'f')

        self.assertEqual(a('_'), '_a')
        self.assertEqual(f('_'), '_f')

        cmp = a_ | f
        self.assertEqual(cmp('_'), '_ab')
        cmp = f | a_ | a_ | f + f
        self.assertEqual(cmp('_'), '_faab_faab')

    def test_node_bracketless(self):
        '''
        I'm allowing the node decorator to be applied without calling because this is how both
        celery and function_pipes work.
        '''
        @node
        def a(x):
            return x + 'a'
        @node()
        def b(x):
            return x + 'b'

        self.assertIsInstance(a, SimpleFunction)
        self.assertIsInstance(b, SimpleFunction)
        self.assertEqual((b|a)('_'), '_ba')

    def test_store(self):
        abc = a | b | store('output') | c

        self.assertEqual(abc('_'), '_abc')
        self.assertEqual(abc.data['output'], '_ab')

    def test_recall(self):
        a.data['k'] = 'secret'

        cmp = a + b | store('k') | c + recall('k')
        self.assertEqual(cmp('_'), '_a_bc_a_b')

        cmp = a + b | store('k') | c + recall('k') | recall('k', from_meta=a)
        self.assertEqual(cmp('_'), 'secret')

    def test_highlight_current_function(self):
        fmt_index = 6

        @node
        def ff(x):
            return x + 'F'

        @node(bind=True)
        def f(meta, x):
            if len(meta._called_functions) == 6:
                location_string = highlight_current_function(meta, use_color=False)
                location_strin_color = highlight_current_function(meta, use_color=True)
                self.assertEqual(location_string, '(a | b | ff | f | f | ->f<- | f | f)')
                self.assertEqual(location_strin_color,
                        '(a | b | ff | f | f | \x1b[31m->f<-\x1b[0m | f | f)')
                self.assertEqual(x, '_abFff')
            return x + 'f'

        pipe = a | b | ff | f | f | f | f | f
        pipe('_')

        af = a + f
        af('_')
        curr_f = highlight_current_function(af)
        self.assertEqual(curr_f, '(a + ->f<-)')

@node
def a(x):
    return x + 'a'
@node()
def b(x):
    return x + 'b'
@node()
def c(x):
    return x + 'c'
