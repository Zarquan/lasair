from __future__ import print_function
import io
import time
import confluent_kafka
from ast import literal_eval
import avroUtils


__all__ = ['EopError', 'AlertConsumer']


class AlertError(Exception):
    """Base class for exceptions in this module.
    """
    pass


class EopError(AlertError):
    """Exception raised when reaching end of partition.

    Parameters
    ----------
    msg : Kafka message
        The Kafka message result from consumer.poll().
    """
    def __init__(self, msg):
        message = 'partition:%d, status:end, ' \
                  'offset:%d, key:%s' \
                  % (msg.partition(),
                     msg.offset(), str(msg.key()))
        self.message = message

    def __str__(self):
        return self.message

def set_offset_beginning(consumer, partitions):
    # force-reset offsets when subscribing to a topic:
    for part in partitions:
        # -2 stands for beginning and -1 for end
        part.offset = -2
    consumer.assign(partitions)

class AlertConsumer(object):
    """Creates an alert stream Kafka consumer for a given topic.

    Parameters
    ----------
    topic : `str`
        Name of the topic to subscribe to.
    schema_files : Avro schema files
        The reader Avro schema files for decoding data. Optional.
    **kwargs
        Keyword arguments for configuring confluent_kafka.Consumer().
    """

    def __init__(self, topic, frombeginning, schema_files=None, **kwargs):
        self.topic = topic
        self.frombeginning = frombeginning
        self.kafka_kwargs = kwargs
        if schema_files is not None:
            self.alert_schema = avroUtils.combineSchemas(schema_files)
        self.raw_msg = None  # added by RDW to keep raw msg

    def __enter__(self):
        self.consumer = confluent_kafka.Consumer(**self.kafka_kwargs)
        if self.frombeginning:
            self.consumer.subscribe([self.topic], on_assign=set_offset_beginning)
        else:
            self.consumer.subscribe([self.topic])
        return self

    def __exit__(self, type, value, traceback):
        # FIXME should be properly handling exceptions here, but we aren't
        self.consumer.close()

    def topics(self):
        t = list(self.consumer.list_topics().topics.keys())
        t.sort()
        return t

    def poll(self, decode=False, verbose=True, timeout=1):
        """Polls Kafka broker to consume topic.

        Parameters
        ----------
        decode : `boolean`
            If True, decodes data from Avro format.
        verbose : `boolean`
            If True, returns every message. If False, only raises EopError.
        """
        msg = self.consumer.poll(timeout)

        if msg:
            if msg.error():
                raise EopError(msg)
            else:
                self.raw_msg = msg.value()   # added by RDW to keep raw msg
                if verbose is True:
                    if decode is True:
                        return self.decodeMessage(msg)
                    else:
                        ast_msg = literal_eval(str(msg.value(), encoding='utf-8'))
                        return ast_msg
        else:
            try:
                raise EopError(msg)
            except AttributeError:
                pass
        return

    def decodeMessage(self, msg):
        """Decode Avro message according to a schema.

        Parameters
        ----------
        msg : Kafka message
            The Kafka message result from consumer.poll().

        Returns
        -------
        `dict`
            Decoded message.
        """
        message = msg.value()
        try:
            bytes_io = io.BytesIO(message)
            decoded_msg = avroUtils.readSchemaData(bytes_io)
            #decoded_msg = avroUtils.readAvroData(bytes_io, self.alert_schema)
        except AssertionError:
            # FIXME this exception is raised but not sure if it matters yet
            bytes_io = io.BytesIO(message)
            decoded_msg = None
        except IndexError:
            literal_msg = literal_eval(str(message, encoding='utf-8'))  # works to give bytes
            bytes_io = io.BytesIO(literal_msg)  # works to give <class '_io.BytesIO'>
            decoded_msg = avroUtils.readSchemaData(bytes_io)  # yields reader
        return decoded_msg
