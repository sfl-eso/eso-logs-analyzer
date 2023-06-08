from pathlib import Path
from typing import Tuple, List


class ChunkMetadata:
    def __init__(self, chunk: Tuple[int, int], offset: int):
        self.chunk_begin = chunk[0]
        self.chunk_end = chunk[1]
        self.offset = offset

    def __str__(self):
        return f"{self.__class__.__name__}(chunk_begin={self.chunk_begin}, chunk_end={self.chunk_end}, offset={self.offset})"

    __repr__ = __str__

    @property
    def num_lines(self):
        return self.chunk_end - self.chunk_begin

    @classmethod
    def load_from_log(cls, path: Path, chunks: List[Tuple[int, int]]):
        from tqdm import tqdm

        data = []
        offset_lines = {chunk[0]: chunk for chunk in chunks}
        # The last chunk ends on the last line
        num_lines = chunks[-1][1]

        with open(path, "r") as log_file:
            progress_bar = tqdm(desc=f"Generating metadata for {path}", total=num_lines)

            # Add the "offset" for the first line
            data.append(ChunkMetadata(offset_lines[0], 0))

            line = log_file.readline()
            line_number = 1
            while line:
                if line_number in offset_lines:
                    data.append(ChunkMetadata(offset_lines[line_number], log_file.tell()))
                line_number += 1
                progress_bar.update(1)
                line = log_file.readline()

        return data
