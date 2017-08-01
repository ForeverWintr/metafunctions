
from metafunctions.util import node, concurrent, mmap

@node
def F(n):
    if n == 0: return 0
    elif n == 1: return 1
    else: return F(n-1)+F(n-2)


multi_fib = mmap(F)

parallel_fib = concurrent(mmap(F))

print(parallel_fib([30, 32, 31]))
#print(multi_fib([30, 32, 31]))

