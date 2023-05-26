from datetime import timedelta, datetime
from typing import Union, Tuple

from colour import Color

from models.postprocessing import CombatEncounter

__SECONDS_IN_A_MINUTE = 60
__RED = Color("#ffaaaa")
__GREEN = Color("#bfffbe")
__INVALID = Color("#ff6ee2")
__GRADIENT = list(__RED.range_to(__GREEN, steps=101))


def __get_color(value: float) -> Color:
    try:
        value = int(value * 100)
        return __GRADIENT[value]
    except IndexError:
        return __INVALID


def __seconds_to_str(seconds: float, decimal_digits: int) -> str:
    if decimal_digits:
        return f"{round(seconds, decimal_digits)}s"
    else:
        # If we don't want decimal digits, we don't need to pass a parameter and the round function returns an integer
        return f"{round(seconds)}s"


def __format_time(seconds: float, decimal_digits: int) -> str:
    if seconds < __SECONDS_IN_A_MINUTE:
        return __seconds_to_str(seconds, decimal_digits)

    minutes = int(seconds // __SECONDS_IN_A_MINUTE)
    seconds = seconds % __SECONDS_IN_A_MINUTE

    return f"{minutes}m{__seconds_to_str(seconds, decimal_digits)}"


def format_uptime(relative_uptime: float, max_uptime: float = 1.0) -> Tuple[str, Color]:
    return "{:.2%}".format(relative_uptime), __get_color(relative_uptime / max_uptime)


def format_time(seconds: Union[float, timedelta, datetime], encounter: CombatEncounter = None, decimal_digits: int = 0) -> str:
    if isinstance(seconds, datetime) and encounter is not None:
        seconds = (seconds - encounter.begin.time).total_seconds()
    elif isinstance(seconds, datetime) and encounter is None:
        raise RuntimeError(f"Can't convert datetime {seconds} to seconds without encounter")

    if isinstance(seconds, timedelta):
        seconds = seconds.total_seconds()

    return __format_time(seconds, decimal_digits)
