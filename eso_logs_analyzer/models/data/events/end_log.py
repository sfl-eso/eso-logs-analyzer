from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    from .begin_log import BeginLog


class EndLog(Event):
    event_type: str = "END_LOG"

    def __init__(self, event_id: int):
        super(EndLog, self).__init__(event_id)

        # The begin log event started this log
        self.begin_log: BeginLog = None
