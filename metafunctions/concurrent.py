import os
import sys
from operator import itemgetter
from multiprocessing import Queue
from collections import namedtuple
import functools
import pickle

from metafunctions.core import FunctionMerge
from metafunctions.core import inject_call_state
from metafunctions import exceptions

# Result tuple to be sent back from workers. Defined at module level for eas of pickling
_ConcurrentResult = namedtuple('_ConcurrentResult', 'index result call_state_data exception')

class ConcurrentMerge(FunctionMerge):

    def __init__(self, function_merge: FunctionMerge):
        '''A subclass of FunctionMerge that calls each of its component functions in parallel.

        ConcurrentMerge takes a FunctionMerge object and upgrades it.
        '''
        if not isinstance(function_merge, FunctionMerge):
            #This check is necessary because functools.wraps will copy FunctionMerge attributes to
            #objects that are not FunctionMerges, so this init will succeed, then result in errors
            #at call time.
            raise exceptions.CompositionError(f'{type(self)} can only upgrade FunctionMerges')

        super().__init__(
                function_merge._merge_func,
                function_merge._functions,
                function_merge._function_join_str)
        self._function_merge = function_merge

    def __str__(self):
        merge_name = str(self._function_merge)
        return f'concurrent{merge_name}' if merge_name.startswith('(') else f'concurrent({merge_name})'

    @inject_call_state
    def __call__(self, *args, **kwargs):
        '''We fork here, and execute each function in a child process before joining the results
        with _merge_func
        '''
        arg_iter, func_iter = self._get_call_iterators(args)
        enumerated_funcs = enumerate(func_iter)
        result_q = Queue()

        #spawn a child for each function
        children = []
        for arg, (i, f) in zip(arg_iter, enumerated_funcs):
            child_pid = self._process_in_fork(i, f, result_q, (arg, ), kwargs)
            children.append(child_pid)

        #iterate over any remaining functions for which we have no args
        for i, f in enumerated_funcs:
            child_pid = self._process_in_fork(i, f, result_q, (), kwargs)
            children.append(child_pid)

        #the parent waits for all children to complete
        for pid in children:
            os.waitpid(pid, 0)

        #then retrieves the results
        results = []
        #iterate over the result q in sorted order
        result_q.put(None)
        for r in sorted(iter(result_q.get, None), key=itemgetter(0)):
            if r.exception:
                raise exceptions.ConcurrentException(
                        'Caught exception in child process') from pickle.loads(r.exception)
            kwargs['call_state'].data.update(pickle.loads(r.call_state_data))
            results.append(pickle.loads(r.result))
        return self._merge_func(*results)

    def _get_call_iterators(self, args):
        return self._function_merge._get_call_iterators(args)

    def _call_function(self, f, args:tuple, kwargs:dict):
        return self._function_merge._call_function(f, args, kwargs)

    def _process_in_fork(self, idx, func, result_q, args, kwargs):
        '''Call self._call_function in a child process. This function returns the ID of the child
        in the parent process, while the child process calls _call_function, puts the results in
        the provided queues, then exits.
        '''
        pid = os.fork()
        if pid:
            return pid

        #here we are the child
        make_result = functools.partial(_ConcurrentResult,
                result=None,
                exception=None,
                index=idx,
                call_state_data=None
        )

        result = None
        try:
            r = self._call_function(func, args, kwargs)

            #pickle here, so that we can't crash with pickle errors in the finally clause
            pickled_r = pickle.dumps(r)
            data = pickle.dumps(kwargs['call_state'].data)
            result = make_result(result=pickled_r, call_state_data=data)
        except Exception as e:
            try:
                # In case func does something stupid like raising an unpicklable exception
                pickled_exception = pickle.dumps(e)
            except AttributeError:
                pickled_exception = pickle.dumps(
                        AttributeError(f'Unplicklable exception raised in {func}'))
            result = make_result(exception=pickled_exception)
        finally:
            result_q.put(result)
            # it's necessary to explicitly close the result_q and join its background thread here,
            # because the below os._exit won't allow time for any cleanup.
            result_q.close()
            result_q.join_thread()

            # This is the one place that the python docs say it's normal to use os._exit. Because
            # this is executed in a child process, calling sys.exit can have unintended
            # consequences. e.g., anything above this that catches the resulting SystemExit can
            # cause the child process to stay alive. the unittest framework does this.
            os._exit(0)

