import csv
import platform
import sys
from pathlib import Path
from typing import Set, Generator, Union


def get_num_lines(file_name: Union[str, Path]) -> int:
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


def __get_sys_max_size():
    """
    Returns the max size for the platform we are running on. For Linux systems its just sys.maxsize, but for Windows,
    the number returned by sys.maxsize won't fit into a C long. Instead, return the max value that fits into a C long in that case.
    @return: The max size for the current platform.
    """
    match platform.system().lower():
        case "linux":
            return sys.maxsize
        case "windows":
            # Bit shift by 31, since in C long is signed
            return (1 << 31) - 1


def read_csv(file_name: str,
             delimiter: str = ",",
             quotechar: str = '"',
             has_header: bool = True,
             columns_to_keep: Set[str] = None) -> Generator[Union[str, dict], None, None]:
    """
    Reads a CSV file in sequence and returns the contents in the form of a generator.
    @param file_name: Name of the file.
    @param delimiter: The CSV delimiter.
    @param quotechar: Character used to encapsulate strings.
    @param has_header: If set to true, the first line will be used as header and each row will be returned as dictionary with the header fields as keys.
    @param columns_to_keep: If non-empty, the returned rows only contain the data for these fields. May only be used with a header.
    @return: The parsed lines in the form of a generator.
    """
    csv.field_size_limit(__get_sys_max_size())
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


def read_csv_chunk(file_name: str, chunk, delimiter: str = ",", quotechar: str = '"') -> Generator[Union[str, dict], None, None]:
    """
    Reads part of a CSV file and returns the contents in the form of a generator.
    @param file_name: Name of the file.
    @param chunk: Chunk that defines part of the file that will be read.
    @param delimiter: The CSV delimiter.
    @param quotechar: Character used to encapsulate strings.
    @return: The parsed lines in the defined chunk in the form of a generator.
    """

    def line_generator(file):
        """
        Reads part of a file and returns each line the form of a generator.
        """
        with open(file, 'r') as file_obj:
            file_obj.seek(chunk.offset)
            num_lines = 0
            while num_lines < chunk.num_lines:
                yield file_obj.readline()
                num_lines += 1

    csv.field_size_limit(__get_sys_max_size())
    data = csv.reader(line_generator(file_name), delimiter=delimiter, quotechar=quotechar)
    for line in data:
        yield line
