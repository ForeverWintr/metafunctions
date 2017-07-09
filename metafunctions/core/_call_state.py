
class CallState:
    __slots__ = (
        'data',
        '_called_functions',
        '_meta_entry'
    )
    def __init__(self):
        '''An object for holding state during a metafunction call.
        '''
        self.data = {}
        self._called_functions = []
        self._meta_entry = None
