
class CallState:
    __slots__ = (
        'data',
        '_called_functions',
        '_meta_entry',
        '_is_active',
        '_exception'
    )
    def __init__(self):
        '''An object for holding state during a metafunction call.
        '''
        self.data = {}
        self._called_functions = []
        self._meta_entry = None
        self._is_active = False
        self._exception = None
