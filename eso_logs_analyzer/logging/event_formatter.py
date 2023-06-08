from logging import Formatter, LogRecord


class EventFormatter(Formatter):

    def __init__(self, *args, **kwargs):
        super().__init__("%(name)s - %(levelname)s - %(asctime)s - %(message)s", *args, **kwargs)

    def format(self, record: LogRecord):
        """
        Format method copied from the default formatter and adjusted accordingly.
        """
        if isinstance(record.msg, tuple) and len(record.msg) == 2:
            return self.__custom_format(record)
        else:
            return super().format(record)

    def __custom_format(self, record: LogRecord):
        event, log_message = record.msg
        # Print the original message
        record.msg = log_message
        record.message = record.getMessage()

        if self.usesTime():
            # Overwrite the log time with the time of the event.
            record.asctime = event.time.strftime(self.default_time_format)

        s = self.formatMessage(record)
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        return s
