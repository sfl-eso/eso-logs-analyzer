import logging

__logger: logging.Logger = None


def create_logger(name="esologs", file="/mnt/g/Jan/Projects/ESOLogs/debug.log", console_level=logging.INFO, file_level=logging.DEBUG):
    # Empty log file
    with open(file, "w") as log_file:
        pass

    # From: https://stackoverflow.com/a/56144390
    logging.basicConfig(level=logging.NOTSET)
    logger = logging.getLogger(name)
    logger.setLevel(console_level)
    file_handler = logging.FileHandler(file)
    file_handler.setLevel(file_level)
    logger.addHandler(file_handler)
    return logger


def logger():
    global __logger
    if __logger is None:
        __logger = create_logger()
    return __logger