import logging
import asapo_consumer
from AsapoWorker.configurable import Configurable, Config
from AsapoWorker.errors import (
    StreamError, ConfigurationError, TemporaryError, MissingDataError,
    EndOfStreamError)

log = logging.getLogger(__name__)


def create_consumer(
        source, path, has_filesystem, beamtime, data_source, token, timeout):
    log.info(
        "Create new consumer (source=%s, path=%s, has_filesystem=%s, "
        "beamtime=%s, data_source=%s, token=%s, timeout=%i).",
        source, path, has_filesystem, beamtime, data_source, token, timeout)
    try:
        consumer = asapo_consumer.create_consumer(
            source, path, has_filesystem, beamtime, data_source, token, timeout)
    except asapo_consumer.AsapoWrongInputError as err:
        raise ConfigurationError("Cannot create consumer") from err
    except asapo_consumer.AsapoConsumerError as err:
        raise StreamError("Cannot create consumer") from err

    return consumer


def create_metadata_consumer(
        source, path, has_filesystem, beamtime, data_source, token, timeout):
    return create_consumer(
        source, path, has_filesystem, beamtime, data_source + "_metadata", token,
        timeout)


@Configurable
class SimpleAsapoReceiver:
    """A simple wrapper for an ASAP::O consumer"""
    consumer = Config(
        "An ASAP::O consumer consumer", type=asapo_consumer.PyConsumer,
        builder=create_consumer, flatten=True, arguments=dict(
            source=Config("ASAP::O endpoint", type=str),
            path=Config("ASAP::O mount path", type=str),
            beamtime=Config("Beamtime ID", type=str),
            token=Config("Beamtime access token", type=str),
            data_source=Config(
                "Name of input data_source", type=str, default=""),
            has_filesystem=Config(
                "Read files directly from filesystem",
                type=bool, default=False),
            timeout=Config(
                "Allowed time in milliseconds for ASAP::O data access before "
                "exception is thrown", type=float, default=3000)
        ))
    group_id = Config(
        "The data_source data is divided between all workers with the same "
        "group_id. If not given, a unique group id will be generated "
        "and the worker will receive the complete data_source.",
        type=str)
    stream = Config(
        "The name of the stream.", type=str, default="default", init=False)
    data_source=Config(
        "Name of input data_source", type=str, default="")

    @group_id.default
    def _generate_group_id(self):
        log.info("Generating new group id.")
        try:
            group_id = self.consumer.generate_group_id()
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError("Cannot generate group_id") from err

        log.info("New group_id=%s.", group_id)
        return group_id

    def get_next(self, meta_only=True):
        log.info("Requesting next record for group_id=%s.", self.group_id)
        try:
            data, metadata = self.consumer.get_next(
                self.group_id, meta_only=meta_only, stream=self.stream)
        except asapo_consumer.AsapoEndOfStreamError as err:
            raise EndOfStreamError("End of data_source") from err
        except (asapo_consumer.AsapoUnavailableServiceError,
                asapo_consumer.AsapoInterruptedTransactionError,
                asapo_consumer.AsapoNoDataError,
                asapo_consumer.AsapoLocalIOError) as err:
            raise TemporaryError("Failed to get next") from err
        except asapo_consumer.AsapoWrongInputError as err:
            raise ConfigurationError("Failed to get next") from err
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError("Failed to get next") from err

        current_id = metadata["_id"]
        log.info("Received record with id=%i.", current_id)

        metadata["stream"] = self.stream
        metadata["data_source"] = self.data_source
        return data, metadata

    def get_current_size(self):
        try:
            return self.consumer.get_current_size(stream=self.stream)
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError("Failed to get current size") from err

    def get_stream_list(self):
        try:
            return self.consumer.get_stream_list()
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError("Failed to get stream list") from err


# TODO: Ensure also that indices are consecutive or start at 0
@Configurable
class SerialAsapoReceiver(SimpleAsapoReceiver):
    """
    A wrapper for an ASAP::O consumer for serial processing

    This wrapper guarantees that the data returned by get_next is in ordered by
    id. If a record cannot be retrieved, get_next raises a MissingDataError and
    continues with the next id on the next call. A MissingDataError is raised
    by get_next exactly once per AsapoReceiver instance for each skipped
    record.
    """
    start_id = Config(
        "The id of the first data to be received. "
        "All earlier data is skipped. "
        "Defaults to start_id=1, i.e., the beginning of the data_source.",
        type=int, default=1)
    max_retries = Config(
        "In case of ASAP::O errors, retry this many times before skipping "
        "data.", type=int, default=2)

    def __attrs_post_init__(self):
        self.expected_id = self.start_id

        if self.start_id != 1:
            self.need_set_marker = True
        else:
            self.need_set_marker = False

        self.retries = 0

    def set_start_id(self, value):
        log.info("Setting new start_id=%s", value)
        self.start_id = value
        self.expected_id = value
        self.need_set_marker = True

    def get_next(self, meta_only=True):
        if self.need_set_marker:
            self._set_marker()
        return self._get_next(meta_only=meta_only)

    def _get_next(self, meta_only):
        log.info("Requesting next record for group_id=%s.", self.group_id)
        try:
            data, metadata = self.consumer.get_next(
                self.group_id, meta_only=meta_only, stream=self.stream)
        except asapo_consumer.AsapoEndOfStreamError as err:
            raise EndOfStreamError(
                "End of data_source at expected_id"
                + str(self.expected_id)) from err
        except asapo_consumer.AsapoUnavailableServiceError as err:
            raise TemporaryError(
                "Failed to get next at expected_id="
                + str(self.expected_id)) from err
        except (asapo_consumer.AsapoInterruptedTransactionError,
                asapo_consumer.AsapoNoDataError,
                asapo_consumer.AsapoLocalIOError) as err:
            self.need_set_marker = True
            self.retries += 1
            raise TemporaryError(
                "Failed to get next at expected_id="
                + str(self.expected_id)) from err
        except asapo_consumer.AsapoWrongInputError as err:
            raise ConfigurationError(
                "Failed to get next at expected_id="
                + str(self.expected_id)) from err
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError(
                "Failed to get next at expected_id="
                + str(self.expected_id)) from err

        current_id = metadata["_id"]
        log.info("Received record with id=%i.", current_id)

        if current_id != self.expected_id:
            self.need_set_marker = True
            self.retries += 1
            raise TemporaryError(
                "Unexpected id, received id={}, expected_id={}".format(
                    current_id, self.expected_id))

        self.expected_id = current_id + 1
        self.retries = 0

        metadata["stream"] = self.stream
        metadata["data_source"] = self.data_source
        return data, metadata

    def _set_marker(self):
        log.info(
            "Setting last read marker to id=%i for group_id=%s.",
            self.expected_id - 1, self.group_id)

        try:
            self.consumer.set_lastread_marker(self.group_id,
                self.expected_id - 1, stream=self.stream)
        except (asapo_consumer.AsapoEndOfStreamError,
                asapo_consumer.AsapoUnavailableServiceError) as err:
            # Do not increase retry counter because get_next will likely
            # error as well
            raise TemporaryError(
                "Failed to set last read marker at expected_id="
                + str(self.expected_id)) from err
        except (asapo_consumer.AsapoInterruptedTransactionError,
                asapo_consumer.AsapoNoDataError,
                asapo_consumer.AsapoLocalIOError) as err:
            if self.retries >= self.max_retries:
                self._handle_too_many_retries(err)
            self.retries += 1
            raise TemporaryError(
                "Failed to set last read marker at expected_id="
                + str(self.expected_id)) from err
        except asapo_consumer.AsapoWrongInputError as err:
            # Do not increase retry counter because get_next will likely
            # error as well
            raise ConfigurationError(
                "Failed to set last read marker at expected_id="
                + str(self.expected_id)) from err
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError(
                "Failed to set last read marker at expected_id="
                + str(self.expected_id)) from err

        if self.retries >= self.max_retries:
            self._handle_too_many_retries()

        self.need_set_marker = False

    def _handle_too_many_retries(self, err=None):
        # There might be a "hole" in the data_source, fall back to get_next
        msg = "Cannot get id={} after retries={}, possible data loss!".format(
            self.expected_id, self.retries)
        self.retries = 0
        self.expected_id += 1
        if err:
            raise MissingDataError(msg) from err
        else:
            raise MissingDataError(msg)

    def get_last(self, meta_only=True):
        log.info("Requesting last record")
        try:
            data, metadata = self.consumer.get_last(meta_only=meta_only, stream=self.stream)
        except (asapo_consumer.AsapoEndOfStreamError,
                asapo_consumer.AsapoUnavailableServiceError) as err:
            raise TemporaryError("Failed to get last") from err
        except (asapo_consumer.AsapoInterruptedTransactionError,
                asapo_consumer.AsapoNoDataError,
                asapo_consumer.AsapoLocalIOError) as err:
            raise MissingDataError("Failed to get last") from err
        except asapo_consumer.AsapoWrongInputError as err:
            raise ConfigurationError("Failed to get last") from err
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError("Failed to get last") from err

        current_id = metadata["_id"]
        log.info("Received last record with id=%i.", current_id)

        # ASAP::O sets the last read marker when calling get_last
        self.need_set_marker = True

        metadata["stream"] = self.stream
        metadata["data_source"] = self.data_source
        return data, metadata


@Configurable
class SerialDatasetAsapoReceiver(SerialAsapoReceiver):
    """
    A wrapper for an ASAP::O consumer for dataset processing

    This wrapper supports functionality of SerialAsapoReceiver but
    expects to receive a dataset 
    """

    def _get_next(self, meta_only):
        log.info("Requesting next dataset for group_id=%s.", self.group_id)
        try:
            message = self.consumer.get_next_dataset(
                      self.group_id, stream=self.stream)

            current_id = message['id']
            metadata = message['content']
            data = None if meta_only else []
            for meta in metadata:
                if not meta_only:
                    data.append(self.consumer.retrieve_data(meta))
                meta['dataset_id'] = current_id
                meta['stream'] = self.stream
                meta['data_source'] = self.data_source
            log.info("Received record with id=%i.", current_id)
        except asapo_consumer.AsapoEndOfStreamError as err:
            raise EndOfStreamError(
                "End of data_source at expected_id"
                + str(self.expected_id)) from err
        except asapo_consumer.AsapoUnavailableServiceError as err:
            raise TemporaryError(
                "Failed to get next at expected_id="
                + str(self.expected_id)) from err
        except (asapo_consumer.AsapoInterruptedTransactionError,
                asapo_consumer.AsapoNoDataError,
                asapo_consumer.AsapoLocalIOError) as err:
            self.need_set_marker = True
            self.retries += 1
            raise TemporaryError(
                "Failed to get next at expected_id="
                + str(self.expected_id)) from err
        except asapo_consumer.AsapoWrongInputError as err:
            raise ConfigurationError(
                "Failed to get next at expected_id="
                + str(self.expected_id)) from err
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError(
                "Failed to get next at expected_id="
                + str(self.expected_id)) from err

        if current_id != self.expected_id:
            self.need_set_marker = True
            self.retries += 1
            raise TemporaryError(
                "Unexpected id, received id={}, expected_id={}".format(
                    current_id, self.expected_id))

        self.expected_id = current_id + 1
        self.retries = 0

        return data, metadata


@Configurable
class AsapoMetadataReceiver:
    """A wrapper for receiving stream metadata of an ASAP::O data_source"""
    consumer = Config(
        "An ASAP::O consumer consumer", type=asapo_consumer.PyConsumer,
        builder=create_consumer, flatten=True, arguments=dict(
            source=Config("ASAP::O endpoint", type=str),
            beamtime=Config("Beamtime ID", type=str),
            token=Config("Beamtime access token", type=str),
            data_source=Config(
                "Name of metadata data_source", type=str, default=""),
            timeout=Config(
                "Allowed time in milliseconds for ASAP::O data access before "
                "exception is thrown", type=float, default=3000),
            path=Config(
                "ASAP::O mount path", type=str, default="", init=False),
            has_filesystem=Config(
                "Read files directly from filesystem",
                type=bool, default=False, init=False)
        ))
    group_id = Config(
        "The data_source data is divided between all workers with the same "
        "group_id. If not given, a unique group id will be generated "
        "and the worker will receive the complete data_source.",
        type=str)

    @group_id.default
    def _generate_group_id(self):
        log.info("Generating new group id.")
        try:
            group_id = self.consumer.generate_group_id()
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError("Cannot generate group_id") from err

        log.info("New group_id=%s.", group_id)
        return group_id

    def get_current_size(self, stream):
        try:
            return self.consumer.get_current_size(stream=stream)
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError("Failed to get current size") from err

    def get_stream_list(self):
        try:
            return self.consumer.get_stream_list()
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError("Failed to get stream list") from err

    def get_stream_metadata(self, stream):
        """
        Return the last available entry from given stream
        of the metadata data_source

        Parameters
        ----------
        stream : str
            Name of stream
        """
        try:
            return self.consumer.get_last(stream=stream)
        except asapo_consumer.AsapoEndOfStreamError as err:
            raise EndOfStreamError("End of metadata data_source") from err
        except (asapo_consumer.AsapoUnavailableServiceError,
                asapo_consumer.AsapoInterruptedTransactionError,
                asapo_consumer.AsapoNoDataError,
                asapo_consumer.AsapoLocalIOError) as err:
            raise TemporaryError("Failed to get stream metadata") from err
        except asapo_consumer.AsapoWrongInputError as err:
            raise ConfigurationError(
                "Failed to get stream metadata") from err
        except asapo_consumer.AsapoConsumerError as err:
            raise StreamError("Failed to get stream metadata") from err
