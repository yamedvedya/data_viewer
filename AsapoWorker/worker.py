import json
from AsapoWorker.data_handler import get_filename_parts
from AsapoWorker.asapo_sender import AsapoSender
from AsapoWorker.configurable import Configurable, Config
from AsapoWorker.errors import ConfigurationError


@Configurable
class Worker:
    sender = Config(
        "An AsapoSender instance used to send process data to a new stream",
        type=AsapoSender, default=None, init=False)
    meta_only = Config(
        "Get only metadata from receiver",
        type=bool, default=False, init=False)

    def handle_error(self):
        pass

    def handle_receiver_error(self):
        self.handle_error()

    def handle_receiver_temporary_error(self):
        self.handle_receiver_error()

    def handle_receiver_missing_data_error(self):
        self.handle_receiver_error()

    def handle_receiver_critical_error(self):
        self.handle_receiver_error()

    def pre_scan(self, data, metadata):
        """
        If metadata strdata_sourceeam is given this function is called at the beginning of
        each stream before get_next is called.

        Parameters
        ----------
        data:
            data of the metadata data_source
        metadata: dict
            metadata of the metadata steam
        """
        pass

    def process(self, data, metadata):
        """
        Function is called each time a new entry from the receiver stream is retrieved
                
        Parameters
        ----------
        data: buffer or list of buffers
            data of the receiver stream
        metadata: dict or list of dicts
            metadata of the receiver steam
        """
        pass

    def shutdown(self):
        """
        Function is called at the end of processing
        """
        pass

    def send(self, data, metadata):
        if self.sender:
            self.sender.send_data(data, metadata)
        else:
            raise ConfigurationError(
                "Worker wants to send data, but no sender configured!")


@Configurable(kw_only=True)
class SimpleWorker(Worker):
    """Worker class for simple, independent processing of single images"""
    output_name_format = Config(
        "Format for deriving output name from input name",
        type=str, default="{basename}_processed-{index}")

    def get_output_name(self, metadata):
        "Get the output name from output_name_format and the input metadata"
        base, index, ext = get_filename_parts(metadata)
        return self.output_name_format.format(
            basename=base, index=index)

    def get_output_type(self):
        "Return the type of the output data. Used as the file extension"
        raise NotImplementedError("Output type not known")

    def get_output_metadata(self, metadata, extra_meta=None):
        """Get output metadata from input metadata

        The new metadata is derived from the given metadata of the input data.
        The record's user metadata is updated with extra_meta, if given.

        Parameters
        ----------
        metadata: dict
            Metadata of the input. The output metadata is derived from this
        extra_meta: dict (optional)
            If given, the 'meta' entry of the output metadata is updated with
            the content of this dict
        """
        input_names = [metadata["name"]]
        input_ids = [metadata["_id"]]
        acknowledged_ids = input_ids
        new_meta = dict(
            input_names=input_names,
            input_ids=input_ids,
            acknowledged_ids=acknowledged_ids)
        if extra_meta:
            new_meta.update(extra_meta)
        new_meta_json = json.dumps(new_meta)
        new_metadata = dict(
            _id=metadata["_id"],
            name=self.get_output_name(metadata) + "." + self.get_output_type(),
            meta=new_meta_json)

        return new_metadata

    def send(self, data, metadata, extra_meta=None):
        """Send the data to the configured output stream

        The metadata and extra_meta arguments are passed to
        get_output_metadata. Its return value is sent as the output metadata.

        Parameters
        ----------
        data: bytes
            The data to send
        metadata: dict
            Metadata of the input. The output metadata is derived from this
        extra_meta: dict (optional)
            If given, the 'meta' entry of the output metadata is updated with
            the content of this dict
        """
        new_metadata = self.get_output_metadata(metadata, extra_meta)

        super().send(data, new_metadata)


@Configurable(kw_only=True)
class SerialWorker(Worker):
    start_id = Config(
        "The id of the first record that will be sent",
        type=int, default=1)
    start_index = Config(
        "The index within a scan of the first record that will be sent",
        type=int, default=0)
    last_id = Config("Id of the last sent record", type=int, init=False)
    last_index = Config(
        "Index within a scan of the last sent record",
        type=int, init=False)

    @last_id.default
    def _last_id_default(self):
        return self.start_id - 1

    @last_index.default
    def _last_index_default(self):
        return self.start_index - 1

    @classmethod
    def calculate_start_ids(cls, last_output_metadata):
        """
        Calculate the start ids for sender and receiver, respectively, from the
        metadata of the last record in the output stream.

        This method is called by the application before data processing begins,
        if neither of the start ids are configured.

        The worker should use any additional information to determing the start
        ids by overwriting this method.

        Parameters
        ----------
        last_output_metadata : dict
            Metadata of the last record in the output stream

        Returns
        -------
        input_start_id : int
            Processing will start with the data at this id
        output_start_id : int
            This id will be assigned to the first data to be sent
        """
        if last_output_metadata:
            last_output_id = last_output_metadata["_id"]
            try:
                last_acknowledged_id = max(
                    last_output_metadata["meta"]["acknowledged_ids"])
            except KeyError:
                last_acknowledged_id = 0
            if last_acknowledged_id < 0:
                raise ValueError(
                    "No valid acknowledged id in last record of output stream "
                    "last_acknowledged_id=%s",
                    last_acknowledged_id)
            input_start_id = last_acknowledged_id + 1
            output_start_id = last_output_id + 1
            return input_start_id, output_start_id
        else:
            return 1, 1

    @classmethod
    def calculate_start_index(cls, last_output_metadata):
        """
        Calculate the start index for the sender from the
        metadata of the last record in the output stream.

        This method is called by the application before data processing begins,
        if the start index is not configured.

        The arguments might be None when called.

        The worker should use any additional information to determing the start
        index by overwriting this method.

        Parameters
        ----------
        last_output_metadata : dict
            Metadata of the last record in the output stream

        Returns
        -------
        start_index : int
            This index will be assigned to the first data to be sent
        """
        if last_output_metadata:
            name = last_output_metadata["name"]
            last_index = int(name.rpartition("-")[-1].split(".")[0])
            return last_index + 1
        else:
            return 0
