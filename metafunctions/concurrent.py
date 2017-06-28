import os
import sys
from operator import itemgetter
from multiprocessing import Queue

from metafunctions.core import FunctionMerge


class ConcurrentMerge(FunctionMerge):
    def __init__(self, function_merge: FunctionMerge):
        '''A subclass of FunctionMerge that calls each of its component functions in parallel.

        ConcurrentMerge takes a FunctionMerge object and upgrades it.
        '''
        self._merge_func = function_merge._merge_func
        self._functions = function_merge._functions
        self._join_str = function_merge._join_str

    def __call__(self, *args, **kwargs):
        '''We fork here, and execute each function in a child process before joining the results
        with _merge_func
        '''
        result_q = Queue()
        #spawn a child for each function
        children = []
        for i, f in enumerate(self.functions):
            pid = os.fork()
            if not pid:
                #we are the child
                self._process_and_die(i, f, result_q, args, kwargs)
            children.append(pid)

        #the parent waits for all children to complete
        for pid in children:
            os.waitpid(pid, 0)

        #then retrieves the results
        result_q.put(None)
        results = [r[1] for r in sorted(iter(result_q.get, None), key=itemgetter(0))]

        return self._merge_func(*results)

    def __str__(self):
        joined_funcs = super().__str__()
        return f"concurrent{joined_funcs}"

    @staticmethod
    def _process_and_die(idx, func, result_q, args, kwargs):
        '''Call the given function with the given args and kwargs, put the result in result_q and
        sysexit.
        '''
        r = func(*args, **kwargs)
        result_q.put((idx, r))

        # it's neccesary to explicitly close the result_q and join its background thread here,
        # because the below os._exit won't allow time for any cleanup.
        result_q.close()
        result_q.join_thread()

        #this is the one place that the python docs say it's normal to use os._exit. Because this
        #is executed in a child process, calling sys.exit can have unintended consequences. e.g.,
        #anything above this that catches the resulting SystemExit can cause the child process to
        #stay alive. the unittest framework does this.
        os._exit(0)
