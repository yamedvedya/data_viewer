class StreamError(RuntimeError):
    pass


class ConfigurationError(StreamError):
    pass


class TemporaryError(StreamError):
    pass


class MissingDataError(StreamError):
    pass


class EndOfStreamError(TemporaryError):
    pass


class StreamFinishedError(StreamError):
    pass

