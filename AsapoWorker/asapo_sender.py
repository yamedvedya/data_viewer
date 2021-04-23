import logging
import threading
import time
import asapo_consumer
import asapo_producer
from AsapoWorker.configurable import Configurable, Config
from AsapoWorker.errors import StreamError, ConfigurationError

log = logging.getLogger(__name__)


def create_producer(
        source, source_type, beamtime, beamline, data_source, token, nthreads=1,
        timeout_producer=30000):
    timeout = timeout_producer/1000
    log.info(
        "Create new producer (source=%s, type=%s, beamtime=%s, beamline=%s, "
        "data_source=%s, token=%s, nthreads=%i, timeout=%s).",
        source, source_type, beamtime, beamline, data_source, token, nthreads, timeout)
    producer = asapo_producer.create_producer(
        source, source_type, beamtime, beamline, data_source, token, nthreads, timeout)
    return producer


def create_consumer(
        source, path, has_filesystem, beamtime, data_source, token,
        timeout_consumer=3000):
    log.info(
        "Create new consumer (source=%s, path=%s, has_filesystem=%s, "
        "beamtime=%s, data_source=%s, token=%s, timeout_consumer=%i).",
        source, path, has_filesystem, beamtime, data_source, token, timeout_consumer)
    try:
        consumer = asapo_consumer.create_consumer(
            source, path, has_filesystem, beamtime, data_source, token,
            timeout_consumer)
    except asapo_consumer.AsapoWrongInputError as err:
        raise ConfigurationError("Cannot create consumer") from err
    except asapo_consumer.AsapoConsumerError as err:
        raise StreamError("Cannot create consumer") from err

    return consumer


def ingest_mode_from_name(name):
    if name in ["DEFAULT", "DEFAULT_INGEST_MODE"]:
        return asapo_producer.DEFAULT_INGEST_MODE
    elif name in ["TRANSFER_DATA", "INGEST_MODE_TRANSFER_DATA"]:
        return asapo_producer.INGEST_MODE_TRANSFER_DATA
    elif name in [
            "TRANSFER_METADATA_ONLY", "INGEST_MODE_TRANSFER_METADATA_ONLY"]:
        return asapo_producer.INGEST_MODE_TRANSFER_METADATA_ONLY
    elif name in ["STORE_IN_FILESYSTEM", "INGEST_MODE_STORE_IN_FILESYSTEM"]:
        return asapo_producer.INGEST_MODE_STORE_IN_FILESYSTEM
    else:
        raise ValueError("Unknown ingest mode: " + str(name))


def convert_ingest_mode(mode):
    try:
        return int(mode)
    except:
        return ingest_mode_from_name(mode)


@Configurable
class AsapoSender:
    producer = Config(
        "An ASAP::O producer", type=asapo_producer.PyProducer,
        builder=create_producer, flatten=True, arguments=dict(
            source=Config("ASAP::O endpoint", type=str),
            source_type=Config("ASAP::O type", type=str),
            beamtime=Config("Beamtime ID", type=str),
            token=Config("Beamtime access token", type=str),
            beamline=Config("Beamline", type=str, default="auto"),
            data_source=Config(
                "Name of output data_source", type=str, default=""),
            nthreads=Config(
                "Number of threads", type=int, default=1),
            timeout_producer=Config(
                "Allowed time in milliseconds for ASAP::O data access before "
                "exception is thrown", type=float, default=30000)
        ))
    consumer = Config(
        "An ASAP::O consumer consumer", type=asapo_consumer.PyConsumer,
        builder=create_consumer, flatten=True, arguments=dict(
            source=Config("ASAP::O endpoint", type=str),
            path=Config("ASAP::O mount path", type=str),
            beamtime=Config("Beamtime ID", type=str),
            token=Config("Beamtime access token", type=str),
            data_source=Config(
                "Name of output data_source", type=str, default=""),
            has_filesystem=Config(
                "Read files directly from filesystem",
                type=bool, default=False),
            timeout_consumer=Config(
                "Allowed time in milliseconds for ASAP::O data access before "
                "exception is thrown", type=float, default=3000)
        ))
    stream = Config(
        "The name of the stream.", type=str, default="default", init=False)
    ingest_mode = Config(
        "The ingest mode determines how the data is handled by ASAP::O. "
        "Also accepts the name of the ingest mode as a string",
        type=int, converter=convert_ingest_mode,
        default="DEFAULT_INGEST_MODE")
    queue_length_threshold = Config(
        "If the length of the sending queue exceeds this value, the call to "
        "send becomes blocking until at least one record is removed from "
        "the queue (by successfully sending or by failure).",
        type=int, default=2)
    retries = Config(
        "Number of retries in case of connection problems",
        type=int, default=3)
    retry_delay = Config(
        "Seconds between retries in case of connection problems",
        type=float, default=3)
    _n_queued = Config(
        "Length of queue of data waiting to be sent", type=int, default=0,
        init=False)
    _lock = Config(
        "Used internally for concurrent access to the n_queued attribute",
        factory=threading.Lock, init=False)
    _group_id = Config(
        "Generated group id for the ASAP::O consumer", type=str, init=False)

    @_group_id.default
    def _generate_group_id(self):
        log.info("Generating new group id.")
        error = None
        for i in range(self.retries):
            try:
                group_id = self.consumer.generate_group_id()
                break
            except asapo_consumer.AsapoConsumerError as err:
                error = err
                if i < self.retries - 1:
                    log.warning("Cannot generate group id, retrying...")
                    time.sleep(self.retry_delay)
        else:
            raise StreamError("Cannot generate group_id") from error

        log.info("New group_id=%s.", group_id)
        return group_id

    def __attrs_post_init__(self):
        log.info("Receiver created with ingest_mode=%s", self.ingest_mode)

    def send_data(self, data, metadata):
        log.info(
            "Sending data with id=%s name=%s",
            metadata["_id"], metadata["name"])
        with self._lock:
            self._n_queued += 1
        try:
            self.producer.send(
                metadata['_id'], metadata['name'], data,
                user_meta=metadata["meta"], ingest_mode=self.ingest_mode,
                stream=self.stream, callback=self._callback)
        except:
            with self._lock:
                self._n_queued -= 1
            raise

        with self._lock:
            n_queued = self._n_queued

        while n_queued > self.queue_length_threshold:
            log.info(
                "Queue length threshold exceeded. Waiting for queued data to "
                "be sent: n_queued=%s queue_length_threshold=%s",
                n_queued, self.queue_length_threshold)
            time.sleep(1)
            with self._lock:
                n_queued = self._n_queued


    def _callback(self, header, err):
        with self._lock:
            assert self._n_queued > 0
            self._n_queued -= 1
        if err:
            log.error(
                "Sending data failed for header=%s with error='%s'",
                header, err)
        else:
            log.info("Successfully sent data for header=%s", header)

    def wait(self, timeout=10):
        with self._lock:
            n_queued = self._n_queued

        if n_queued > 0:
            log.info(
                "Waiting for queued data to be sent: n_queued=%s timeout=%s",
                n_queued, timeout)

            start = time.time()
            while time.time() - start < timeout:
                with self._lock:
                    if self._n_queued == 0:
                        break
                time.sleep(1)

            with self._lock:
                n_queued = self._n_queued

            if n_queued > 0:
                raise TimeoutError(
                    "Remaining {} item(s) couldn't be sent within {}s".format(
                        n_queued, timeout))
            else:
                log.info("Successfully finished sending all queued data")

    def get_last(self, meta_only=True):
        log.info("Requesting last record")
        try:
            data, metadata = self.consumer.get_last(meta_only=meta_only, stream=self.stream)
        except asapo_consumer.AsapoEndOfStreamError:
            return None, None
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError("Failed to get last") from err

        current_id = metadata["_id"]
        log.info("Received last record with id=%i.", current_id)

        return data, metadata

    def get_stream_list(self):
        try:
            return self.consumer.get_stream_list()
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError("Failed to get stream list") from err
