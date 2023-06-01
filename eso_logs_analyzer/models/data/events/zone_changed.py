from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import ZoneDifficulty
from .event import Event

if TYPE_CHECKING:
    from ..encounter_log import EncounterLog


class ZoneChanged(Event):
    event_type: str = "ZONE_CHANGED"

    def __init__(self, id: int, encounter_log: EncounterLog, event_id: int, zone_id: str, zone_name: str, difficulty: str):
        super(ZoneChanged, self).__init__(id, encounter_log, event_id)
        # Id of the zone the player changed to
        self.zone_id = int(zone_id)
        # Name of the zone the player changed to
        self.zone_name = zone_name
        # Difficulty of the instance or zone
        self.difficulty: ZoneDifficulty = ZoneDifficulty(difficulty)
