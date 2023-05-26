from datetime import timedelta, datetime
from typing import Union

from models.postprocessing import CombatEncounter

SECONDS_IN_A_MINUTE = 60


def __seconds_to_str(seconds: float, decimal_digits: int) -> str:
    if decimal_digits:
        return f"{round(seconds, decimal_digits)}s"
    else:
        # If we don't want decimal digits, we don't need to pass a parameter and the round function returns an integer
        return f"{round(seconds)}s"


def __format_time(seconds: float, decimal_digits: int) -> str:
    if seconds < SECONDS_IN_A_MINUTE:
        return __seconds_to_str(seconds, decimal_digits)

    minutes = int(seconds // SECONDS_IN_A_MINUTE)
    seconds = seconds % SECONDS_IN_A_MINUTE

    return f"{minutes}m{__seconds_to_str(seconds, decimal_digits)}"


def format_uptime(relative_uptime: float, max_uptime: float = 1.0) -> str:
    # TODO: color gradient


def format_time(seconds: Union[float, timedelta, datetime], encounter: CombatEncounter = None, decimal_digits: int = 0) -> str:
    if isinstance(seconds, datetime) and encounter is not None:
        seconds = (seconds - encounter.begin.time).total_seconds()
    elif isinstance(seconds, datetime) and encounter is None:
        raise RuntimeError(f"Can't convert datetime {seconds} to seconds without encounter")

    if isinstance(seconds, timedelta):
        seconds = seconds.total_seconds()

    return __format_time(seconds, decimal_digits)
