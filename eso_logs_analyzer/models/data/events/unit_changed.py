from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import Hostility, RaceId, ClassId
from .event import Event

if TYPE_CHECKING:
    from .unit_added import UnitAdded


class UnitChanged(Event):
    event_type: str = "UNIT_CHANGED"

    def __init__(self,
                 event_id: int,
                 unit_id: str,
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
        super(UnitChanged, self).__init__(event_id)
        # Id of the unit
        self.unit_id = int(unit_id)
        # Name of the unit
        self.name = name
        # Account name including @, if the unit is a pllayer
        self.account = account
        # Level (up to 50) of the unit
        self.level = int(level)
        # CP Points of the unit, if the unit is a player
        self.champion_level = int(champion_level)
        # Hostility of the unit (enemy, pet, player, etc.)
        self.hostility: Hostility = Hostility(hostility)

        # Class of the unit
        self.class_id: ClassId = ClassId(class_id)
        # Race of the unit
        self.race_id: RaceId = RaceId(race_id)
        # Numerical string that identifies this player
        self.character_id = character_id
        # If non-zero the unit id of the unit that owns this unit
        self.owner_unit_id = int(owner_unit_id)
        # If true, the unit is in a group with the recording player
        self.is_grouped_with_local_player = self._convert_boolean(is_grouped_with_local_player, "is_grouped_with_local_player")

        # Corresponding event that added the unit this event affects
        self.unit_added: UnitAdded = None

    # def __str__(self):
    #     return f"{self.__class__.__name__}(id={self.id}, unit_id={self.unit_id}, name={self.name}, " \
    #            f"account={self.account}, level={self.level}, champion_level={self.champion_level}, " \
    #            f"hostility={self.hostility}, unit_added={self.unit_added is not None})"
    #
    # __repr__ = __str__
