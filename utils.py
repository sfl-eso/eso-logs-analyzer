import sys
import csv
from datetime import datetime
from typing import Set


def read_csv(file_name: str,
             delimiter: str = ",",
             quotechar: str = '"',
             has_header: bool = True,
             columns_to_keep: Set[str] = None) -> list:
    lines = []
    csv.field_size_limit(sys.maxsize)
    with open(file_name, 'r') as file:
        data: csv.DictReader = csv.reader(file, delimiter=delimiter, quotechar=quotechar)
        if has_header:
            header = next(data)
            for row in data:
                padded_row = row
                for _ in range(len(header) - len(row)):
                    padded_row.append(None)
                named_row = {name: padded_row[index] for index, name in enumerate(header)}
                if columns_to_keep:
                    named_row = {key: value for key, value in named_row.items() if key in columns_to_keep}
                lines.append(named_row)
        else:
            lines = [row for row in data]
    return lines


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
