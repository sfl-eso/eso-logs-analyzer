from __future__ import annotations

from typing import TYPE_CHECKING

from utils import parse_epoch_time
from .enums import Server, Locale
from .event import Event

if TYPE_CHECKING:
    from .end_log import EndLog


class BeginLog(Event):
    event_type: str = "BEGIN_LOG"

    def __init__(self, id: int, epoch_time: str, log_version: str, server: str, locale: str, client_version: str):
        super(BeginLog, self).__init__(id)
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

    # TODO: unified event time method in Event using "parent" events
    # def event_time(self, event_id: int) -> datetime:
    #     return self.time + timedelta(milliseconds=(event_id - self.id))
