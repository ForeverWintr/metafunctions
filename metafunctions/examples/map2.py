from metafunctions.util import node, mmap
import time

# 'heavy lifting' functions

@node
def process_thing(x):
    time.sleep(1)

process_thing(2)