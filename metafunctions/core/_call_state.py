
class CallState:
    __slots__ = (
        'data',
        '_called_functions',
    )
    def __init__(self):
        '''An object for holding state during a metafunction call.
        '''
        self.data = {}
        self._called_functions = []
