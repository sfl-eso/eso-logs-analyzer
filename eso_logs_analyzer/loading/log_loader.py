from pathlib import Path
from typing import Union, List

from eso_logs_analyzer.loading.utils import get_num_lines, read_csv
from eso_logs_analyzer.models import Base
from eso_logs_analyzer.models.data import EncounterLog
from eso_logs_analyzer.models.data.events import Event, ErrorEventStub, EndLog
from eso_logs_analyzer.utils import tqdm


class LogLoader(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __init__(self, file: Union[str, Path], multiple: bool = False, *args, **kwargs):
        """
        Loads an encounterlog file into one or multiple logs.
        @param file: File containing the encounter log data. Loads the file in parallel chunks.
        @param multiple: If set to True, if multiple logs are in a single file, they will be loaded and their encounters chained together.
        """
        super().__init__(*args, **kwargs)

        self.file = Path(file).absolute()
        assert self.file.exists() and self.file.is_file(), f"File {file} does not exist or is not a file!"
        self.num_lines = get_num_lines(self.file)
        self.multiple = multiple

    def _load_line(self, current_id, current_log, line) -> Event:
        try:
            return Event.create(current_id, current_log, int(line[0]), line[1], *line[2:])
        except ValueError as e:
            return ErrorEventStub(current_id, None, int(line[0]), e, line[1:])

    def _load_log(self) -> List[EncounterLog]:
        csv_file = read_csv(str(self.file), has_header=False)
        events = []
        current_id = 0
        logs = []

        current_log = EncounterLog()

        for line in tqdm(csv_file, desc=f"Parsing log {self.file}", total=self.num_lines):
            event = self._load_line(current_id, current_log, line)
            events.append(event)
            current_id += 1

            # Separate logs into different objects if there are multiple logs in the file
            if isinstance(event, EndLog):
                current_log.events = events
                logs.append(current_log)
                if self.multiple:
                    # We have a separate log starting after this line
                    events = []
                    current_id = 0
                    current_log = EncounterLog()
                else:
                    break
        return logs

    def parse_log(self) -> Union[EncounterLog, List[EncounterLog]]:
        """
        Parses an encounterlog file into one or multiple logs depending on the passed parameters and how many logs are contained in the file.
        @return: A single or multiple encounter log objects, depending on the number of logs in the input file.
        """

        logs = self._load_log()

        # Initialize log by processing all the events in the log.
        # If this step is skipped, the log object contains no useful data.
        for log in logs:
            log.initialize()

        # Make sure that the index for each event equals the event's id.
        self.logger.info("Validating event indices")
        for log in logs:
            assert all([event.id == index for index, event in enumerate(log.events)]), f"Not all event ids equal the indices of the events " \
                                                                                       f"for log {log}"

        return logs if self.multiple else logs[0]
