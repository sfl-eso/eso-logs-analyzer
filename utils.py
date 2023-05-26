import csv
import json
import sys
from datetime import datetime
from typing import Set, Generator, Union

_ability_map = None


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


def ability_map():
    global _ability_map
    if _ability_map is None:
        _ability_map = json.load(open("ability_map.json"))
    return _ability_map
