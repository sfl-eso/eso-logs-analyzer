from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    from .begin_combat import BeginCombat
    from ..encounter_log import EncounterLog


class EndCombat(Event):
    event_type: str = "END_COMBAT"

    def __init__(self, id: int, encounter_log: EncounterLog, event_id: int):
        super(EndCombat, self).__init__(id, encounter_log, event_id)
        self.begin_combat: BeginCombat = None
