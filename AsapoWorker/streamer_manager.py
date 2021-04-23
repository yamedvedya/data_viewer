from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict
import logging
import time
from threading import Lock, Event
from AsapoWorker.utils import format_error, not_last_n

log = logging.getLogger(__name__)


class StreamerManager:
    def __init__(self, create_streamer, max_streams=16):
        self._create_streamer = create_streamer
        self.max_streams = max_streams
        # Temporarily, there can be more than max_streams threads,
        # therefore the thread pool should be a bit larger
        # (number of additional threads chosen by fair dice roll)
        self.executor = ThreadPoolExecutor(max_workers=max_streams + 4)
        self.streamers = OrderedDict()
        self.futures = OrderedDict()
        self.stopped = Event()
        self.lock = Lock()
        self.initialized = False

    def initialize(self):
        # Create first streamer to trigger errors with create_streamer early
        streamer = self._create_streamer()

        with self.lock:
            self.streamers[streamer.receiver.stream] = streamer

        self.initialized = True

    def start_stream_thread(self, stream):
        with self.lock:
            if stream not in self.streamers and not self.stopped.is_set():
                log.info("Starting new stream=%s", stream)
                streamer = self._create_streamer(stream=stream)
                future = self.executor.submit(streamer.run)
                self.streamers[stream] = streamer
                self.futures[stream] = future

    def stop_old_streamers(self, n_max):
        with self.lock:
            for streamer in not_last_n(n_max, self.streamers.values()):
                log.info("Stopping stream=%s", streamer.receiver.stream)
                streamer.stop()

    def cleanup_stopped_streamers(self):
        with self.lock:
            finished_streams = []
            for stream, future in self.futures.items():
                if future.done():
                    # Deleting items of the iterator here could break the loop
                    finished_streams.append(stream)
                    err = future.exception()
                    if err:
                        log.error(
                            "stream {}  stopped with error: ".format(
                                stream) + format_error(err))
                        # Stop application
                        self.stopped.set()

            for stream in finished_streams:
                del self.futures[stream]
                del self.streamers[stream]

    def stop(self):
        self.stopped.set()

    def _shutdown(self):
        self.executor.shutdown()

    def run(self):
        if not self.initialized:
            self.initialize()

        # start initial streamer
        with self.lock:
            if not self.stopped.is_set():
                for stream, streamer in self.streamers.items():
                    log.info(
                        "Starting new stream=%s",
                        streamer.receiver.stream)
                    self.futures[stream] = (
                        self.executor.submit(streamer.run))

        while True:
            if self.stopped.wait(0.5):
                self.stop_old_streamers(n_max=0)
                time.sleep(0.5)  # replace wait which now returns immediately
            else:
                self.stop_old_streamers(n_max=self.max_streams)

            self.cleanup_stopped_streamers()

            if not self.futures:
                break

        self._shutdown()
