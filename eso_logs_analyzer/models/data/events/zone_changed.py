from .enums import ZoneDifficulty
from .event import Event


class ZoneChanged(Event):
    event_type: str = "ZONE_CHANGED"

    def __init__(self, event_id: int, zone_id: str, zone_name: str, difficulty: str):
        super(ZoneChanged, self).__init__(event_id)
        # Id of the zone the player changed to
        self.zone_id = int(zone_id)
        # Name of the zone the player changed to
        self.zone_name = zone_name
        # Difficulty of the instance or zone
        self.difficulty: ZoneDifficulty = ZoneDifficulty(difficulty)
