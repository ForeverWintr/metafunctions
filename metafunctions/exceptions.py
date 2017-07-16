

class MetaFunctionError(Exception):
    pass

class ConcurrentException(MetaFunctionError):
    pass

class BroadcastError(MetaFunctionError, ValueError):
    #e.g., trying to broadcast more inputs than can be recieved by functions
    pass
