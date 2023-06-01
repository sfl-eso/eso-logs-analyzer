from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    from .unit_added import UnitAdded
    from ..encounter_log import EncounterLog


class UnitRemoved(Event):
    event_type: str = "UNIT_REMOVED"

    def __init__(self, id: int, encounter_log: EncounterLog, event_id: int, unit_id: str):
        super(UnitRemoved, self).__init__(id, encounter_log, event_id)
        # Id of the unit that was removed
        self.unit_id = int(unit_id)

        # Corresponding unit added event
        self.unit_added: UnitAdded = None
