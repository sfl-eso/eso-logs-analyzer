from logging import Logger

from ..log import get_logger, get_event_logger


class Base(object):
    __logger: Logger = None
    __event_logger: Logger = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    @property
    def logger(cls):
        if cls.__logger is None:
            cls.__logger = get_logger(cls.__name__)
        return cls.__logger

    @classmethod
    @property
    def event_logger(cls):
        if cls.__event_logger is None:
            cls.__event_logger = get_event_logger(cls.__name__)
        return cls.__event_logger
