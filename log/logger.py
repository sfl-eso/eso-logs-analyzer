import logging
import sys

from python_json_config import Config
from python_json_config.config_node import ConfigNode

from .event_formatter import EventFormatter

__LOG_INITIALIZED = False
__LOG_CONFIG: ConfigNode = None


def __empty_log_file():
    global __LOG_CONFIG
    with open(__LOG_CONFIG.file, "w"):
        pass


def __log_formatter() -> logging.Formatter:
    """
    Customize the format of the log output.
    Valid parameters are documented at https://docs.python.org/3/library/logging.html#logrecord-attributes
    """
    return logging.Formatter("%(name)s - %(levelname)s - %(asctime)s - %(message)s")


def init_loggers(config: Config):
    global __LOG_INITIALIZED, __LOG_CONFIG
    if not __LOG_INITIALIZED:
        __LOG_INITIALIZED = True
        __LOG_CONFIG = config.logging
        __empty_log_file()

        # Initialize logging with basic configuration values before we instantiate later loggers.
        # See https://stackoverflow.com/a/56144390
        # We add our custom formatter to the root logger, so all other loggers (including the one injected by tqdm)
        # will inherit this formatter
        logging.basicConfig(level=logging.NOTSET)
        logging.root.handlers[0].setFormatter(__log_formatter())


def get_logger(name: str, console_level=None, file_level=None):
    global __LOG_CONFIG
    # logging.getLevelName maps from level to name and from name to level
    # Log level 0 indicates the log level is unset. In that we also set the level to the pre-defined one
    console_level = console_level or logging.getLevelName(__LOG_CONFIG.console_level)
    file_level = file_level or logging.getLevelName(__LOG_CONFIG.file_level)

    logger = logging.getLogger(name=name)
    logger.setLevel(console_level)

    # Also log to the log file with a different level
    # TODO: log level for file handler does not work properly
    file_handler = logging.FileHandler(__LOG_CONFIG.file)
    file_handler.setLevel(file_level)
    file_handler.setFormatter(__log_formatter())
    logger.addHandler(file_handler)

    return logger


def get_event_logger(name: str, console_level=None):
    global __LOG_CONFIG
    # logging.getLevelName maps from level to name and from name to level
    # Log level 0 indicates the log level is unset. In that we also set the level to the pre-defined one
    console_level = console_level or logging.getLevelName(__LOG_CONFIG.console_level)

    logger = logging.getLogger(name=f"{name}.EventLogger")
    # Disable this logger propagating its messages to its parent loggers (such as the root logger)
    # Disabling this avoids printing each message twice (https://stackoverflow.com/a/44426266)
    logger.propagate = False
    logger.handlers.clear()
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(console_level)
    stream_handler.setFormatter(EventFormatter())
    logger.addHandler(stream_handler)

    return logger
