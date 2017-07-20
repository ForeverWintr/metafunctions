
from metafunctions.util import node, concurrent

@node
def F(n):
    if n == 0: return 0
    elif n == 1: return 1
    else: return F(n-1)+F(n-2)


multi_fib = F & F & F

parallel_fib = concurrent(F & F & F)

print('Multi')
#print(parallel_fib(30))
print(multi_fib(30))

