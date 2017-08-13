
class CallState:
    __slots__ = (
        'data',
        '_meta_stack',
        '_exception',
        '_exception_meta_stack',
    )
    def __init__(self):
        '''An object for holding state during a metafunction call.'''
        self.data = {}
        self._meta_stack = []
        self._exception = None
        self._exception_meta_stack = None

    def set_exception(self, exception):
        '''
        Called to indicate that an exception has occured on this call_state. Saves the exception,
        as well as freezes a copy of the meta_stack where the exception occured.
        '''
        if exception is not self._exception:
            self._exception = exception
            self._exception_meta_stack = tuple(self._meta_stack)
