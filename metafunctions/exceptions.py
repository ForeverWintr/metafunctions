class MetaFunctionError(Exception):
    pass


class CompositionError(MetaFunctionError, TypeError):
    "An exception that occureds when MetaFunctions are composed incorrectly"
    pass


class CallError(MetaFunctionError, TypeError):
    "An exception that occures when a MetaFunction is called incorrectly"

    def __init__(self, *args, location: str = ""):
        self.location = location
        super().__init__(*args)

    def __repr__(self):
        return "{}({}, {})".format(
            self.__class__.__name__,
            self.args,
            "location='{}'".format(self.location) if self.location else "",
        )


class ConcurrentException(CallError):
    "Concurrent specific call errors (e.g., things that aren't picklable)"
