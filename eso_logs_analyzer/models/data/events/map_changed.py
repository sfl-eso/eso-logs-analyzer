from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    from ..encounter_log import EncounterLog


class MapChanged(Event):
    event_type: str = "MAP_CHANGED"

    def __init__(self, id: int, encounter_log: EncounterLog, event_id: int, map_id: str, map_name: str, texture_path: str):
        super(MapChanged, self).__init__(id, encounter_log, event_id)
        # Id of the map that the player changed to
        self.map_id = int(map_id)
        # Name of the map the player changed to
        self.map_name = map_name
        # The map's icon
        self.map_icon = texture_path
