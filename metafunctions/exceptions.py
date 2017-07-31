class MetaFunctionError(Exception):
    pass


class CompositionError(MetaFunctionError, TypeError):
    "An exception that occureds when MetaFunctions are composed incorrectly"
    pass


class CallError(MetaFunctionError, TypeError):
    "An exception that occures when a MetaFunction is called incorrectly"
    pass


class ConcurrentException(CallError):
    "Concurrent specific call errors (e.g., things that aren't picklable)"
    pass

