from logging import Logger

from log import get_logger


class Base(object):
    __logger: Logger = None

    def __init__(self):
        super().__init__()
        # self.__init_logger()

    # @classmethod
    # def __init_logger(cls):
    #     if cls.logger is None:
    #         cls.logger = get_logger(cls.__name__)

    @classmethod
    @property
    def logger(cls):
        if cls.__logger is None:
            cls.__logger = get_logger(cls.__name__)
        return cls.__logger
