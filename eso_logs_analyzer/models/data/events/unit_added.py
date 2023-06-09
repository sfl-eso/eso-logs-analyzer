from __future__ import annotations

from typing import TYPE_CHECKING, List

from .enums import UnitType, RaceId, ClassId, Hostility
from .event import Event
from .span_event import SpanCast

if TYPE_CHECKING:
    from .unit_changed import UnitChanged
    from .unit_removed import UnitRemoved
    from ..encounter_log import EncounterLog


class UnitAdded(SpanCast):
    """
    Represent the spawn of a unit. Can be player, enemy or pet.
    """
    event_type: str = "UNIT_ADDED"

    def __init__(self,
                 id: int,
                 encounter_log: EncounterLog,
                 event_id: int,
                 unit_id: str,
                 unit_type: str,
                 is_local_player: str,
                 player_per_session_id: str,
                 monster_id: str,
                 is_boss: str,
                 class_id: str,
                 race_id: str,
                 name: str,
                 account: str,
                 character_id: str,
                 level: str,
                 champion_level: str,
                 owner_unit_id: str,
                 hostility: str,
                 is_grouped_with_local_player: str):
        super(UnitAdded, self).__init__(id, encounter_log, event_id)
        # If of the unit
        self.unit_id = int(unit_id)
        # What kind of unit this is (player, monster)
        self.unit_type: UnitType = UnitType(unit_type)
        # Name of the unit
        self.name = name
        # Account name containing @, if this unit is a player
        self.account = account
        # Level of this unit
        self.level = int(level)
        # CP points, if this unit is a player
        self.champion_level = int(champion_level)
        # Hostility of this unit (ally, hostile)
        self.hostility: Hostility = Hostility(hostility)

        # If true, this unit is the recording player
        self.is_local_player = self._convert_boolean(is_local_player, "is_local_player")
        # Id of the player in the session
        self.player_per_session_id = int(player_per_session_id)
        # If this unit is a monster, its id
        self.monster_id = int(monster_id)
        # If true, this unit is a boss enemy
        self.is_boss = self._convert_boolean(is_boss, "is_boss")
        # Class id of the unit
        self.class_id: ClassId = ClassId(class_id)
        # Race id of the unit
        self.race_id: RaceId = RaceId(race_id)
        # Numerical string that identifies this player
        self.character_id = character_id
        # Unit id of the owner if this unit has an owner
        self.owner_unit_id = int(owner_unit_id)
        # True if this unit is grouped with the recording player
        self.is_grouped_with_local_player = self._convert_boolean(is_grouped_with_local_player, "is_grouped_with_local_player")

        # All events of this unit changing
        self.unit_changed: List[UnitChanged] = []
        # Corresponding event of this unit being removed
        self.unit_removed: UnitRemoved = None
        # Unit object of the owner if it exists
        self.owner_unit: UnitAdded = None

    @property
    def end_event(self) -> Event:
        return self.unit_removed

    @end_event.setter
    def end_event(self, value: Event):
        self.unit_removed = value
