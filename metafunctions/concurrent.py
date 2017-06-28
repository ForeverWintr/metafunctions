import os
import sys
from operator import itemgetter
from multiprocessing import Queue
import queue

from metafunctions.core import FunctionMerge
from metafunctions.util import highlight_current_function
from metafunctions.exceptions import ConcurrentException


class ConcurrentMerge(FunctionMerge):
    def __init__(self, function_merge: FunctionMerge):
        '''A subclass of FunctionMerge that calls each of its component functions in parallel.

        ConcurrentMerge takes a FunctionMerge object and upgrades it.
        '''
        super().__init__(
                function_merge._merge_func,
                function_merge._functions,
                function_merge._join_str)

    def __str__(self):
        joined_funcs = super().__str__()
        return f"concurrent{joined_funcs}"

    def __call__(self, *args, **kwargs):
        '''We fork here, and execute each function in a child process before joining the results
        with _merge_func
        '''
        self._modify_kwargs(kwargs)
        result_q = Queue()
        error_q = Queue()

        #spawn a child for each function
        children = []
        for i, f in enumerate(self.functions):
            pid = os.fork()
            if not pid:
                #we are the child
                self._process_and_die(i, f, result_q, error_q, args, kwargs)
            children.append(pid)

        #the parent waits for all children to complete
        for pid in children:
            os.waitpid(pid, 0)

        #then retrieves the results
        try:
            error = error_q.get_nowait()
        except queue.Empty:
            pass
        else:
            raise ConcurrentException('Caught exception in child process') from error

        result_q.put(None)
        results = [r[1] for r in sorted(iter(result_q.get, None), key=itemgetter(0))]

        return self._merge_func(*results)

    @staticmethod
    def _process_and_die(idx, func, result_q, error_q, args, kwargs):
        '''This function is only called by child processes. Call the given function with the given
        args and kwargs, put the result in result_q, then die.
        '''
        try:
            r = func(*args, **kwargs)
        except Exception as e:
            error_q.put(e)
        else:
            result_q.put((idx, r))
        finally:
            # it's neccesary to explicitly close the result_q and join its background thread here,
            # because the below os._exit won't allow time for any cleanup.
            result_q.close()
            error_q.close()
            result_q.join_thread()
            error_q.join_thread()

            # This is the one place that the python docs say it's normal to use os._exit. Because
            # this is executed in a child process, calling sys.exit can have unintended
            # consequences. e.g., anything above this that catches the resulting SystemExit can
            # cause the child process to stay alive. the unittest framework does this.
            os._exit(0)

