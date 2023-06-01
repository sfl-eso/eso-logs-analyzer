from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..encounter_log import EncounterLog
    from .event import Event


class AbstractEvent(object):
    def __init__(self, id: int, encounter_log: EncounterLog, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Line number in the source log file. Represents index in list of events in encounterlog
        self.id = id
        self.encounter_log = encounter_log

    @property
    def previous(self) -> Optional[Event]:
        if self.id > 0:
            return self.encounter_log.events[self.id - 1]

    @property
    def next(self) -> Optional[Event]:
        if (self.id + 1) < len(self.encounter_log.events):
            return self.encounter_log.events[self.id + 1]
