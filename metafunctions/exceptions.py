class MetaFunctionError(Exception):
    pass

class CompositionError(MetaFunctionError, TypeError):
    "An exception that occureds when MetaFunctions are composed incorrectly"
    pass


class CallError(MetaFunctionError, TypeError):
    "An exception that occures when a MetaFunction is called incorrectly"
    def __init__(self, arg, location: str=''):
        self.location = location
        super().__init__(arg)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.args}, location={self.location})'

class ConcurrentException(CallError):
    "Concurrent specific call errors (e.g., things that aren't picklable)"


