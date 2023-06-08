from pathlib import Path
from typing import Union, List, Tuple, Dict

from .chunk_metadata import ChunkMetadata
from .log_loader import LogLoader
from .utils import read_csv_chunk
from ..models.data import EncounterLog
from ..models.data.events import Event, EndLog
from ..parallel import ResultCollector, ParallelTask


class ChunkIterator(object):
    """
    Iterates through events that are separated into multiple chunks.
    Allows iteration through chunks without having to copy the events into a separate unified list.
    """

    def __init__(self, chunks: List[Tuple[int, int]], event_chunks: Dict[Tuple[int, int], List[Event]]):
        self.chunks = sorted(chunks, key=lambda t: t[0])
        self.event_chunks = event_chunks

    def __iter__(self):
        for chunk in self.chunks:
            for event in self.event_chunks[chunk]:
                yield event


class LogCollector(ResultCollector):
    """
    Collects chunks of an encounter log loaded in parallel and aggregates the results.
    """

    def __init__(self, chunks: List[Tuple[int, int]]):
        super().__init__()
        self.event_chunks: Dict[Tuple[int, int], List[Event]] = {}
        # Create a copy of the chunks list to make sure we are using a different object.
        self.chunks = list(chunks)

    def collect_result(self, result):
        result_chunk, result_events = result
        self.event_chunks[result_chunk] = result_events

    def aggregated_result(self):
        return ChunkIterator(self.chunks, self.event_chunks)

    def is_completed(self) -> bool:
        return all([chunk in self.event_chunks for chunk in self.chunks])


class ParallelLoader(LogLoader):

    def __init__(self, file: Union[str, Path], multiple: bool = False, num_processes: int = 8, num_chunks: int = 64):
        """
        Loads an encounterlog file into one or multiple logs in parallel.
        @param file: File containing the encounter log data. Loads the file in parallel chunks.
        @param multiple: If set to True, if multiple logs are in a single file, they will be loaded and their encounters chained together.
        @param num_processes: How many processes should be used.
        @param num_chunks: In how many parts the input file should be read. Should always be higher than the number of processes for performance reasons.
        """
        super().__init__(file=file, multiple=multiple)
        self.num_processes = num_processes
        self.num_chunks = num_chunks

        self.input_chunks = self.compute_chunks()
        # TODO: load from cache
        self.chunk_metadata: List[ChunkMetadata] = ChunkMetadata.load_from_log(self.file, self.input_chunks)

    def compute_chunks(self) -> List[Tuple[int, int]]:
        """
        Splits the input file into the defined amount of chunks. Each chunk is a tuple defining the interval [start, stop).
        May produce one more chunk than defined, if the number of lines is not divisible by the number of chunks.
        @return: List of consecutive chunks.
        """
        chunk_size = int(self.num_lines / self.num_chunks)
        input_chunks = []
        id_offset = 0
        while id_offset < self.num_lines:
            chunk_end = min(id_offset + chunk_size, self.num_lines)
            input_chunks.append((id_offset, chunk_end))
            id_offset = chunk_end

        return input_chunks

    def _load_log(self) -> List[EncounterLog]:
        def read_log_chunk(chunk: ChunkMetadata, path: Path):
            csv_chunk = read_csv_chunk(str(path), chunk=chunk)
            current_id = chunk.chunk_begin
            events = []

            for line in csv_chunk:
                try:
                    # We don't have a log to pass to the event yet.
                    events.append(self._load_line(current_id, None, line))
                except IndexError as e:
                    self.logger.error(f"Error {e} parsing line {current_id}: {line}")
                finally:
                    current_id += 1

            return (chunk.chunk_begin, chunk.chunk_end), events

        read_log_task = ParallelTask(description=f"Reading log file {self.file}",
                                     num_processes=self.num_processes,
                                     input_objects=self.chunk_metadata,
                                     task_function=read_log_chunk,
                                     result_collector=LogCollector(self.input_chunks),
                                     task_function_kwargs={
                                         "path": self.file
                                     })
        chunk_iterator = read_log_task.execute()
        events = []

        logs = []
        id_offset = 0
        current_log = EncounterLog()
        self.logger.info("Aggregating events")
        for index, event in enumerate(chunk_iterator):
            # Reset the ids to 0 starting at each begin log event to ensure that the ids equal their index in the event list.
            event.id = event.id - id_offset
            # Set the log object, since it could not be done when reading the file and creating the object.
            event.encounter_log = current_log
            events.append(event)

            # Separate logs into different objects if there are multiple logs in the file
            if isinstance(event, EndLog):
                current_log.events = events[id_offset:index + 1]
                logs.append(current_log)
                if self.multiple:
                    # We have a separate log starting after this line
                    events = []
                    id_offset = index + 1
                    current_log = EncounterLog()
                else:
                    break
        return logs
