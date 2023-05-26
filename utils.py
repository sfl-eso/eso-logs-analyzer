import csv
import sys
from datetime import datetime
from typing import Set, Generator, Union

_ability_map = None


def tqdm(iterable=None, desc=None, total=None, leave=True, file=None,
         ncols=None, mininterval=0.1, maxinterval=10.0, miniters=None,
         ascii=None, disable=False, unit='it', unit_scale=False,
         dynamic_ncols=False, smoothing=0.3, bar_format=None, initial=0,
         position=None, postfix=None, unit_divisor=1000, write_bytes=False,
         lock_args=None, nrows=None, colour=None, delay=0, gui=False,
         **kwargs):
    """
    Wrapper for tqdm that uses the logging_redirect_tqdm functionality to allow logging with tqdm progress bars
    while maintaining the same tqdm api.
    See https://tqdm.github.io/docs/contrib.logging/
    """
    import tqdm as o_tqdm
    from tqdm.contrib.logging import logging_redirect_tqdm
    with logging_redirect_tqdm():
        for obj in o_tqdm.tqdm(iterable=iterable, desc=desc, total=total, leave=leave, file=file,
                               ncols=ncols, mininterval=mininterval, maxinterval=maxinterval, miniters=miniters,
                               ascii=ascii, disable=disable, unit=unit, unit_scale=unit_scale,
                               dynamic_ncols=dynamic_ncols, smoothing=smoothing, bar_format=bar_format, initial=initial,
                               position=position, postfix=postfix, unit_divisor=unit_divisor, write_bytes=write_bytes,
                               lock_args=lock_args, nrows=nrows, colour=colour, delay=delay, gui=gui,
                               **kwargs):
            yield obj


def get_num_lines(file_name: str) -> int:
    """
    Fast counting of the number of lines in large files (https://stackoverflow.com/a/9631635).
    """

    def blocks(file, size=65536):
        while True:
            b = file.read(size)
            if not b:
                break
            yield b

    with open(file_name, "r", encoding="utf-8", errors="ignore") as f:
        return sum(bl.count("\n") for bl in blocks(f))


def read_csv(file_name: str,
             delimiter: str = ",",
             quotechar: str = '"',
             has_header: bool = True,
             columns_to_keep: Set[str] = None) -> Generator[Union[str, dict], None, None]:
    csv.field_size_limit(sys.maxsize)
    with open(file_name, 'r') as file:
        data = csv.reader(file, delimiter=delimiter, quotechar=quotechar)
        if has_header:
            header = next(data)
            for row in data:
                padded_row = row
                for _ in range(len(header) - len(row)):
                    padded_row.append(None)
                named_row = {name: padded_row[index] for index, name in enumerate(header)}
                if columns_to_keep:
                    named_row = {key: value for key, value in named_row.items() if key in columns_to_keep}
                yield named_row
        else:
            for line in data:
                yield line


def parse_epoch_time(epoch_time: str) -> datetime:
    return datetime.fromtimestamp(int(epoch_time) / 1000)


def all_subclasses(cls):
    classes = []
    for subclass in cls.__subclasses__():
        if subclass.event_type is not None:
            classes.append(subclass)
        else:
            classes.extend(all_subclasses(subclass))
    return classes
