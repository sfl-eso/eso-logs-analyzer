from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    from .begin_log import BeginLog
    from ..encounter_log import EncounterLog


class EndLog(Event):
    event_type: str = "END_LOG"

    def __init__(self, id: int, encounter_log: EncounterLog, event_id: int):
        super(EndLog, self).__init__(id, encounter_log, event_id)

        # The begin log event started this log
        self.begin_log: BeginLog = None
