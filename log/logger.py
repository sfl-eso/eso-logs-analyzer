import logging

from python_json_config import Config
from python_json_config.config_node import ConfigNode

__LOG_INITIALIZED = False
__LOG_CONFIG: ConfigNode = None


def __empty_log_file():
    global __LOG_CONFIG
    with open(__LOG_CONFIG.file, "w"):
        pass


def init_loggers(config: Config):
    global __LOG_INITIALIZED, __LOG_CONFIG
    if not __LOG_INITIALIZED:
        __LOG_INITIALIZED = True
        __LOG_CONFIG = config.logging
        __empty_log_file()


def get_logger(name: str, console_level=None, file_level=None):
    global __LOG_CONFIG
    # logging.getLevelName maps from level to name and from name to level
    # Log level 0 indicates the log level is unset. In that we also set the level to the pre-defined one
    console_level = console_level or logging.getLevelName(__LOG_CONFIG.console_level)
    file_level = file_level or logging.getLevelName(__LOG_CONFIG.file_level)

    # From: https://stackoverflow.com/a/56144390
    logging.basicConfig(level=logging.NOTSET)
    logger = logging.getLogger(name=name)
    # logger.handlers.clear()
    logger.setLevel(console_level)
    file_handler = logging.FileHandler(__LOG_CONFIG.file)
    file_handler.setLevel(file_level)
    logger.addHandler(file_handler)
    return logger
