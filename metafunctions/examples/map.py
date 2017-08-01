from metafunctions.util import node, mmap

@node
def a(x):
    return x + 'a'

batman = 'nnnnnnnn' | mmap(a) | ''.join

print(str(batman))
print(f'{batman()} batman!')

### Equivalent to:

result = ''.join(map(a, 'nnnnnnnn'))

