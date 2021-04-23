import argparse
import logging
import signal
import sys
from AsapoWorker.configuration import (
    create_instance_from_configurable,
    create_cli_parser_from_configurable_class,
    parsed_args_to_dict)
from AsapoWorker.streamer import Streamer
from AsapoWorker.streamer_manager import StreamerManager
from AsapoWorker.errors import StreamError

log = logging.getLogger(__name__)


class Application:
    def __init__(
            self, worker_class, consumer_class,
            producer_class=None, metadata_receiver_class=None,
            verbose=False, log_level=logging.WARN):
        self.worker_class = worker_class
        self.consumer_class = consumer_class
        self.producer_class = producer_class
        self.metadata_receiver_class = metadata_receiver_class
        self.receiver_consumer = None
        self.sender_consumer = None
        self.sender_producer = None
        self.metadata_receiver = None
        self.options = None
        self.streamer_manager = StreamerManager(self._create_streamer)
        self.verbose = verbose
        self.log_level = log_level
        self.initialized = False

    def initialize(self):
        self._parse_options()

        self._setup_logging()

        self.streamer_manager.initialize()

        def signalhandler(signum, frame):
            self.streamer_manager.stop()

        signal.signal(signal.SIGINT, signalhandler)
        signal.signal(signal.SIGTERM, signalhandler)

        self.initialized = True

    def _parse_options(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument(
            "-v", "--verbose", action='store_const', dest="log_level",
            const="INFO", default=argparse.SUPPRESS,
            help="Log more information (same as --log_level INFO)")

        parser.add_argument(
            "--log_level", default="WARNING", choices=[
                "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set log level for the application")

        parser.add_argument(
            "--delay_on_error", type=float, default=1, metavar="FLOAT",
            help="When an error occurs, wait so many seconds before retrying")

        parser.add_argument(
            "--fix_metadata_stream", type=bool, default=False, metavar="BOOL",
            help="Always use 'default' stream of the metadata data_source")

        parser.add_argument(
            "--stream_naming_scheme", type=str, default="numeric",  choices=[
                "numeric", "date", "basename"],
            help="Scheme to chose new stream name")

        parser.add_argument(
            "--stream", type=str, default="default", metavar="STR",
            help="The stream where streaming should start")

        create_cli_parser_from_configurable_class(
            self.consumer_class, parser, prefix="receiver.")
        create_cli_parser_from_configurable_class(
            self.worker_class, parser, prefix="worker.")

        if self.producer_class:
            create_cli_parser_from_configurable_class(
                self.producer_class, parser, prefix="sender.")

        if self.metadata_receiver_class:
            create_cli_parser_from_configurable_class(
                self.metadata_receiver_class, parser,
                prefix="metadata_receiver.")

        parsed_args = parser.parse_args(sys.argv[1:])

        self.options = parsed_args_to_dict(parsed_args)

        # Ensure that options always contains the necessary keys, even if the
        # corresponding configurable class has no arguments
        for key in ["worker", "sender"]:
            if key not in self.options:
                self.options[key] = {}

    def _setup_logging(self):
        log_level = self.options["log_level"]
        format = (
            "%(asctime)s %(threadName)s AsapoWorker %(filename)s:%(lineno)d "
            "%(levelname)-8s %(message)s")
        logging.basicConfig(level=log_level, format=format)
        logging.info("Log level set to %s", log_level)

    # TODO: resusing the same consumer and sender objects for all threads relies
    # on an implementation detail of create_instance_from_configurable
    def _create_streamer(self, stream=None):
        if self.receiver_consumer:
            kwargs = {"consumer": self.receiver_consumer}
        else:
            kwargs = {}

        consumer = create_instance_from_configurable(
            self.consumer_class, self.options["receiver"], kwargs=kwargs)

        if not self.receiver_consumer:
            self.receiver_consumer = consumer.consumer

        if self.producer_class:
            if self.sender_consumer:
                assert self.sender_producer is not None
                kwargs = {
                    "consumer": self.sender_consumer,
                    "producer": self.sender_producer}
            else:
                kwargs = {}

            sender = create_instance_from_configurable(
                self.producer_class, self.options["sender"], kwargs=kwargs)

            if not self.sender_consumer:
                self.sender_consumer = sender.consumer
                self.sender_producer = sender.producer
        else:
            sender = None

        if self.metadata_receiver_class:
            if not self.metadata_receiver:
                self.metadata_receiver = create_instance_from_configurable(
                    self.metadata_receiver_class,
                    self.options["metadata_receiver"])

        if not stream:
            if "stream" in self.options:
                stream = self.options["stream"]

        if stream:
            log.info("Setting stream=%s", stream)
            consumer.stream = stream
            if sender:
                sender.stream = stream

        _set_start_position(
            self.options, consumer, sender, self.worker_class)

        worker = create_instance_from_configurable(
            self.worker_class, self.options["worker"])

        # The start position (provided by the user or calculated from the
        # acknowledged id) was used to create the worker and must be reset.
        # This means that for all but the first worker the user provided start
        # id will be ignored and the start id will be calculated from the
        # acknowledged ids
        _unset_start_position(self.options)

        if sender:
            worker.sender = sender

        streamer_options = {}
        if "delay_on_error" in self.options:
            streamer_options ["delay_on_error"] = self.options["delay_on_error"]
        if "stream_naming_scheme" in self.options:
            streamer_options ["stream_naming_scheme"] = \
                self.options["stream_naming_scheme"]
        if "fix_metadata_stream" in self.options:
            streamer_options["fix_metadata_stream"] = \
                self.options["fix_metadata_stream"]

        streamer = Streamer(
            consumer, worker, metadata_receiver=self.metadata_receiver,
            end_of_stream_callback=self.streamer_manager.start_stream_thread,
            **streamer_options)

        return streamer

    def run(self):
        if not self.initialized:
            self.initialize()

        self.streamer_manager.run()


def _set_start_position(options, consumer, sender, worker_class):
    if ("start_id" not in options["worker"]
            or "start_id" not in options["receiver"]
            or "start_index" not in options["worker"]):
        if ("start_id" in options["worker"]
                or "start_id" in options["receiver"]):
            raise ValueError(
                "The start id must be given for either both or none of "
                "the receiver and worker")
        if ("start_id" in options["worker"]
                or "start_index" in options["worker"]):
            raise ValueError(
                "If one of start id or start index for the worker is given, "
                "the other must be given as well")

        if sender:
            try:
                _, last_output_metadata = sender.get_last()
            except StreamError as err:
                log.warning(
                    "Retrieving last output data failed with err=%s", err)
                last_output_metadata = None
        else:
            last_output_metadata = None

        if last_output_metadata:
            try:
                input_start_id, output_start_id = (
                    worker_class.calculate_start_ids(last_output_metadata))

                output_start_index = worker_class.calculate_start_index(
                    last_output_metadata)
            except AttributeError:
                log.warning(
                    "Worker does not support starting from the last processed "
                    "record. Starting from the beginning instead")
            else:
                consumer.set_start_id(input_start_id)

                log.info(
                    "Setting worker option start_id=%s", output_start_id)
                options["worker"]["start_id"] = output_start_id

                log.info(
                    "Setting worker option start_index=%s", output_start_index)
                options["worker"]["start_index"] = output_start_index


def _unset_start_position(options):
    for key in ["start_id", "start_index"]:
        for section in ["receiver", "worker"]:
            try:
                del options[section][key]
            except KeyError:
                pass
