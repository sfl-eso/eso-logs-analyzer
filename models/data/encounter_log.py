from pathlib import Path
from typing import Union

from tqdm import tqdm

from utils import read_csv
from .events import Event, EndLog


class EncounterLog(object):

    @classmethod
    def parse_log(cls, file: Union[str, Path], multiple: bool = False):
        path = Path(file)
        path = path.absolute()
        csv_file = read_csv(str(path), has_header=False)
        events = []
        count = 0
        logs = []
        previous_event = None

        for line in tqdm(csv_file, desc=f"Parsing log {path}"):
            event = Event.create(count, int(line[0]), line[1], *line[2:])
            if event is None:
                continue
            if previous_event is not None:
                event.previous = previous_event
            events.append(event)
            previous_event = event
            count += 1
            if isinstance(event, EndLog):
                logs.append(events)
                if multiple:
                    # We have a separate log starting after this line
                    events = []
                    count = 0
                    previous_event = None
                else:
                    break

        # logs = [cls(events) for events in logs]
        # return logs if multiple else logs[0]
