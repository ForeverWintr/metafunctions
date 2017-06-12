
from metafunctions.tests.util import BaseTestCase
from metafunctions.decorators import node
from metafunctions import util

class TestUnit(BaseTestCase):
    def test_store(self):
        abc = a | b | util.store('output') | c

        self.assertEqual(abc('_'), '_abc')
        self.assertEqual(abc.data['output'], '_ab')

    def test_recall(self):
        a.data['k'] = 'secret'

        cmp = a + b | util.store('k') | c + util.recall('k')
        self.assertEqual(cmp('_'), '_a_bc_a_b')

        cmp = a + b | util.store('k') | c + util.recall('k') | util.recall('k', from_meta=a)
        self.assertEqual(cmp('_'), 'secret')

    def test_highlight_current_function(self):
        fmt_index = 6

        @node
        def ff(x):
            return x + 'F'

        @node(bind=True)
        def f(meta, x):
            if len(meta._called_functions) == 6:
                location_string = util.highlight_current_function(meta, use_color=False)
                location_strin_color = util.highlight_current_function(meta, use_color=True)
                self.assertEqual(location_string, '(a | b | ff | f | f | ->f<- | f | f)')
                self.assertEqual(location_strin_color,
                        '(a | b | ff | f | f | \x1b[31m->f<-\x1b[0m | f | f)')
                self.assertEqual(x, '_abFff')
            return x + str(f)

        pipe = a | b | ff | f | f | f | f | f
        pipe('_')


@node
def a(x):
    return x + 'a'
@node()
def b(x):
    return x + 'b'
@node()
def c(x):
    return x + 'c'
