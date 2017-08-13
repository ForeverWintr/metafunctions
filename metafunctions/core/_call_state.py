
class CallState:
    __slots__ = (
        'data',
        '_meta_stack',
        '_meta_entry',
        '_is_active',
        '_exception'
    )
    def __init__(self):
        '''An object for holding state during a metafunction call.
        '''
        self.data = {}
        self._meta_stack = []
        self._meta_entry = None
        self._is_active = False
        self._exception = None
