from __future__ import annotations

from typing import TYPE_CHECKING, List

from .abstract_ability import AbstractEvent
from .event import Event

if TYPE_CHECKING:
    from ..encounter_log import EncounterLog


class ErrorEventStub(Event, AbstractEvent):
    """
    Event stub that is inserted when a line in the encounter log cannot be parsed into an event. Allows iteration through the events in the manner
    of a linked list and ensures the event ids correspond to their line numbers.
    """

    def __init__(self, id: int, encounter_log: EncounterLog, event_id: int, error, data: List[str]):
        super().__init__(id, encounter_log, event_id, *data)
        self.error = error

        self.logger.error(f"Could not create Event of type {data[0]} at line {self.id + 1}! {self.error}")
