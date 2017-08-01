from metafunctions.util import node, mmap

@node
def a(x):
    return x + 'a'

add_a = (a & a & a) | ''.join
print('banana:', add_a(*'bnn')) #banana: banana


# What if we want to call `a` for each input?
''.join(map(a, 'nnnnnnnn'))

batman = mmap(a) | ''.join

print(f'{batman("nnnnnnnn")} batman!') # nananananananana batman!


