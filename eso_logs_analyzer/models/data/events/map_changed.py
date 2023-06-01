from .event import Event


class MapChanged(Event):
    event_type: str = "MAP_CHANGED"

    def __init__(self, event_id: int, map_id: str, map_name: str, texture_path: str):
        super(MapChanged, self).__init__(event_id)
        # Id of the map that the player changed to
        self.map_id = int(map_id)
        # Name of the map the player changed to
        self.map_name = map_name
        # The map's icon
        self.map_icon = texture_path
