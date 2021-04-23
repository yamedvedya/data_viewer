import logging
import random
import asapo_consumer

# use this logger to get output in order
log = logging.getLogger(__name__)


class DummyStream:
    def __init__(self, metadata, data=None):
        if data is None:
            data = [0]*len(metadata)
        if len(data) != len(metadata):
            raise ValueError("data and metadata lengths differ")
        self.data = data
        self.metadata = metadata
        self.indices = {}

    def get_next(self, group_id, stream="default", meta_only=True):
        if stream != "default":
            raise asapo_consumer.AsapoEndOfStreamError("End of stream")
        index = self.indices.setdefault(group_id, 1)
        if index > len(self.data):
            raise asapo_consumer.AsapoEndOfStreamError("End of stream")

        metadata = self.metadata[index - 1]
        if meta_only:
            data = None
        else:
            data = self.data[index - 1]
        self.indices[group_id] += 1
        return data, metadata

    def get_next_ok(self, group_id, stream="default", meta_only=True):
        log.info("get_next_ok")
        return self.get_next(group_id, stream=stream, meta_only=meta_only)

    def get_next_end_of_stream(
            self, group_id, stream="default", meta_only=True):
        log.info("get_next_end_of_stream")
        raise asapo_consumer.AsapoEndOfStreamError("End of stream")

    def get_next_skip(self, group_id, stream="default", meta_only=True):
        log.info("get_next_skip")
        self.indices[group_id] = self.indices.get(group_id, 0) + 1
        raise asapo_consumer.AsapoInterruptedTransactionError("Interrupted")

    def get_next_no_skip(self, group_id, stream="default", meta_only=True):
        log.info("get_next_no_skip")
        raise asapo_consumer.AsapoInterruptedTransactionError("Interrrupted")

    def get_next_no_data(self, group_id, stream="default", meta_only=True):
        log.info("get_next_no_data")
        raise asapo_consumer.AsapoNoDataError("No data")

    def get_next_unavailable(
            self, group_id, stream="default", meta_only=True):
        log.info("get_next_unavailable")
        raise asapo_consumer.AsapoUnavailableServiceError("Unavailable")

    def get_next_io_error(self, group_id, stream="default", meta_only=True):
        log.info("get_next_io_error")
        raise asapo_consumer.AsapoUnavailableServiceError("IO error")

    def get_next_consumer_error(
            self, group_id, stream="default", meta_only=True):
        log.info("get_next_consumer_error")
        raise asapo_consumer.AsapoConsumerError()

    def set_lastread_marker(self, group_id, id, stream="default"):
        if stream != "default":
            return
        self.indices[group_id] = id + 1

    def set_lastread_marker_ok(self, id, group_id, stream="default"):
        log.info("set_lastread_marker_ok")
        return self.set_lastread_marker(id, group_id, stream=stream)

    def set_lastread_marker_not_set(self, id, group_id, stream="default"):
        log.info("set_lastread_marker_not_set")
        raise asapo_consumer.AsapoInterruptedTransactionError("Interrrupted")

    def set_lastread_marker_set(self, id, group_id, stream="default"):
        log.info("set_lastread_marker_set")
        self.set_lastread_marker(id, group_id)
        raise asapo_consumer.AsapoInterruptedTransactionError("Interrrupted")

    def set_lastread_marker_unavailable(
            self, id, group_id, stream="default"):
        log.info("set_lastread_marker_unavailable")
        raise asapo_consumer.AsapoUnavailableServiceError("Unavailable")


def call_iterator(funcs, obj=None, method=None):
    """
    Return a function that calls one of the arguments (in the given order) when
    called.

    Example
    -------
    caller = call_iterator(f, g, h)
    caller(1, foo=2) # returns f(1, foo=2)
    caller() # returns g()
    caller("bar") # returns h("bar")
    caller(1) # raises StopIteration
    """
    if obj is not None:
        if method is not None:
            funcs = [getattr(obj, method + "_" + func) for func in funcs]
        else:
            funcs = [getattr(obj, func) for func in funcs]

    func_iter = iter(funcs)

    def caller(*args, **kwargs):
        f = next(func_iter)
        return f(*args, **kwargs)

    return caller


def choices(population, k):
    return [random.choice(population) for i in range(k)]
