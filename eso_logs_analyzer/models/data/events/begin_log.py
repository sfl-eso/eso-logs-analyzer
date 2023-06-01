from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import Server, Locale
from .event import Event
from .span_event import SpanCast
from ....utils import parse_epoch_time

if TYPE_CHECKING:
    from .end_log import EndLog
    from ..encounter_log import EncounterLog


class BeginLog(SpanCast):
    event_type: str = "BEGIN_LOG"

    def __init__(self, id: int, encounter_log: EncounterLog, event_id: int, epoch_time: str, log_version: str, server: str, locale: str, client_version: str):
        super(BeginLog, self).__init__(id, encounter_log, event_id)
        # The time at which the log starts
        self.time = parse_epoch_time(epoch_time)
        # The server on which the log was created. Can be
        self.server: Server = Server(server)
        # The language of the game
        self.locale: Locale = Locale(locale)
        # Version of the game
        self.client_version = client_version
        # Version of the log
        self.log_version = log_version

        # The event that finishes this log
        self.end_log: EndLog = None

    @property
    def end_event(self) -> Event:
        return self.end_log

    @end_event.setter
    def end_event(self, value: Event):
        self.end_log = value
