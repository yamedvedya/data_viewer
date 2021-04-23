import logging
import traceback
from threading import Event
import threading
from asapo_producer import AsapoProducerError
from AsapoWorker.configuration import create_instance_from_configurable
from AsapoWorker.configurable import check_type
from AsapoWorker.errors import (
    TemporaryError, MissingDataError, ConfigurationError, EndOfStreamError,
    StreamError)
from AsapoWorker.utils import format_error

log = logging.getLogger(__name__)


def max_stream(streams):
    return max(int(s) for s in streams if s.isdecimal())


def get_new_stream(stream, stream_list, metadata_stream_list,
                      sender_stream_list=None, naming_scheme='date'):
    """
    Get name of next stream using one of naming scheme

    Scheme 'date': streams name encoded timestamp and therefore
        can be ordered from earliest to latest. Next stream is one, which is
        next in the stream_list compared to current stream

    Scheme 'basename': list of streamer and receiver streams are compared.
        Next stream is one, which is present in the receiver stream list and
        not present in the sender stream list.

    Scheme 'numeric': Assume the name of stream is an integer, which increases
        for each next stream a newer stream is ready, when it has data and metadata

    Parameters
    ----------
    stream: str
        Name of current stream
    stream_list: list of str
        List of receiver streams
    metadata_stream_list: list of str
        List of metadata-stream streams
    sender_stream_list: list of str
        List of sender streams
    naming_scheme: str
        Naming scheme to chose next stream
    """

    if naming_scheme == 'basename':
        if sender_stream_list is None:
            log.warning(
                "Cannot calculate next stream. sender stream list is None"
                "stream=%s", stream)
            return None

        new_streams = list(set(stream_list)
                              - set(sender_stream_list) - set(stream))
        if len(new_streams) > 0:
            return new_streams[0]
    elif naming_scheme == 'date':

        if stream not in stream_list:
            pos = 0
        else:
            pos = sorted(stream_list).index(stream) + 1
        if pos < len(stream_list):
            return sorted(stream_list)[pos]

    elif naming_scheme == 'numeric':
        max_stream_number = max_stream(stream_list)
        try:
            if (int(stream) < max_stream_number
                    and max_stream_number in metadata_stream_list):
                return str(int(stream) + 1)
        except ValueError:
            log.warning(
                "Cannot calculate next stream from non-integer value "
                "stream=%s", stream)
    else:
        log.warning(
            "Unknown stream naming scheme {naming_scheme}".format(
                naming_scheme=naming_scheme))
        return None

    return None


class ContainsAll:
    def __contains__(self, item):
        return True


class Streamer:
    def __init__(
            self, receiver, worker, metadata_receiver=None, delay_on_error=3,
            end_of_stream_callback=None, fix_metadata_stream=False,
            stream_naming_scheme='numeric'):
        self.receiver = receiver
        self.worker = worker
        self.metadata_receiver = metadata_receiver
        self.initial_delay_on_error = delay_on_error
        self.delay_on_error = delay_on_error
        self.end_of_stream_callback = end_of_stream_callback
        self.likely_done = False
        self.fix_metadata_stream = fix_metadata_stream
        self.stopped = Event()
        self.stream_naming_scheme = stream_naming_scheme

    def _process_stream(self):
        data, metadata = self._get_next()

        if metadata is None:
            return False

        try:
            self.worker.process(data, metadata)
        except (AsapoProducerError, ConfigurationError) as err:
            log.critical("Sending failed: " + str(err))
            raise err
        except Exception as err:
            log.exception("Worker could not process data.")
            raise err

        return True

    def _get_stream_metadata(self):
        try:
            if self.fix_metadata_stream:
                stream = 'default'
            else:
                stream = self.receiver.stream
            return self.metadata_receiver.get_stream_metadata(
                stream)
        except EndOfStreamError as err:
            log.info(format_error(err))
            # The stream might have been skipped
            self._handle_end_of_stream()
            return None, None
        except TemporaryError as err:
            log.warn(format_error(err))
            return None, None

    def _get_next(self):
        try:
            data, metadata = self.receiver.get_next(meta_only=self.worker.meta_only)
        except EndOfStreamError as err:
            log.info(format_error(err))
            self._handle_receiver_temporary_error()
            self._handle_end_of_stream()
            return None, None
        except TemporaryError as err:
            log.warn(format_error(err))
            self._handle_receiver_temporary_error()
            return None, None
        except MissingDataError as err:
            log.error("Missing data error", exc_info=True)
            self._handle_receiver_missing_data_error()
            return None, None
        except Exception as err:
            log.critical("Unhandled exception", exc_info=True)
            self._handle_receiver_critical_error()
            raise err

        return data, metadata

    def _handle_end_of_stream(self):
        # When receiving an EndOfStreamError, there are two cases to consider:
        # 1. The stream has data and metadata, i.e., occurs in the stream
        #    list
        #    -> data receiving is slow or stream is finished
        #    -> start next stream
        # 2. A newer stream has data and metadata, i.e., occurs in the
        #    stream list
        #    -> stream is likely finished or was skipped
        #    -> start next stream + reduce polling rate
        if self.likely_done:
            # nothing is left to be done
            return

        try:
            stream_list = self.receiver.get_stream_list()
        except StreamError:
            # the state is unknown, so nothing should be done
            log.warn("Failed to get stream list", exc_info=True)
            return

        if self.worker.sender is not None:
            try:
                sender_stream_list = self.worker.sender.get_stream_list()
            except StreamError:
                log.warn(
                    "Failed to get sender stream list", exc_info=True)
                return
        else:
            sender_stream_list = None

        if self.metadata_receiver:
            try:
                metadata_stream_list = (
                    self.metadata_receiver.get_stream_list())
            except StreamError:
                # the state is unknown, so nothing should be done
                log.warn(
                    "Failed to get metadata stream list", exc_info=True)
                return
        else:
            # Data_source does not use stream metadata, therefore consider all
            # metadata as available
            metadata_stream_list = ContainsAll()

        if (self.receiver.stream in stream_list
                and self.receiver.stream in metadata_stream_list):
            has_data = True
        else:
            has_data = False

        try:
            new_stream = get_new_stream(
                self.receiver.stream, stream_list,
                metadata_stream_list,
                sender_stream_list,
                self.stream_naming_scheme)
        except ValueError:
            # stream is not an integer, so nothing should be done
            return

        if (has_data or new_stream is not None) and self.end_of_stream_callback:
            # call the callback only once
            print("Start next: ", new_stream)
            self.end_of_stream_callback(new_stream['name'])
            self.end_of_stream_callback = None

        if new_stream is not None:
            self.likely_done = True

    def _handle_receiver_temporary_error(self):
        self.worker.handle_receiver_temporary_error()

    def _handle_receiver_missing_data_error(self):
        self.worker.handle_receiver_missing_data_error()

    def _handle_receiver_critical_error(self):
        self.worker.handle_receiver_critical_error()

    def run(self):
        try:
            threading.current_thread().name = "stream_{}".format(
                self.receiver.stream)
            if self.metadata_receiver:
                log.info("Waiting for stream metadata")
                while not self.stopped.is_set():
                    data, stream_metadata = self._get_stream_metadata()
                    if stream_metadata:
                        self._reset_delay_on_error()
                        break
                    if self.likely_done:
                        self.stopped.wait(self.delay_on_error)
                        self._increase_delay_on_error()
                else:
                    # no break, i.e., stopped is set
                    return

                log.info("Performing pre-scan setup")
                parameters = self._meta_to_parameters(stream_metadata['meta'])
                self.worker.pre_scan(data, stream_metadata, parameters)

            log.info("Start stream processing.")
            while not self.stopped.is_set():
                success = self._process_stream()
                if self.likely_done and not success:
                    self.stopped.wait(self.delay_on_error)
                    self._increase_delay_on_error()
                else:
                    self._reset_delay_on_error()
        except Exception as e:
            log.error(f"Streamer fails with error : {e}", exc_info=True)
            raise
        finally:
            self._shutdown()

    def _meta_to_parameters(self, metadata):
        parameters = None
        if hasattr(self.worker, "Parameters"):
            parameters = create_instance_from_configurable(self.worker.Parameters, metadata)
            check_type(parameters)
        return parameters

    def _increase_delay_on_error(self):
        self.delay_on_error = max(
            10*(self.initial_delay_on_error),
            self.delay_on_error + self.initial_delay_on_error)

    def _reset_delay_on_error(self):
        self.delay_on_error = self.initial_delay_on_error

    def stop(self):
        log.info("Stopping stream processing.")
        self.stopped.set()

    def _shutdown(self):
        log.info("Cleaning up.")
        self.worker.shutdown()
        if self.worker.sender:
            try:
                self.worker.sender.wait(timeout=10)
            except Exception as err:
                log.error("Possible data loss:" + str(err))
