

class MetaFunctionError(Exception):
    pass

class ConcurrentException(MetaFunctionError):
    pass

class CompositionError(MetaFunctionError, TypeError):
    pass
