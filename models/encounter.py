from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .meta_events import BeginCombat, EndCombat
    from .unit_events import UnitAdded


class Encounter(object):
    def __init__(self, begin_combat: BeginCombat):
        self.begin_combat = begin_combat

    @property
    def end_combat(self) -> EndCombat:
        return self.begin_combat.end_combat

    @property
    def start_time(self) -> datetime:
        return self.begin_combat.time

    @property
    def duration(self) -> timedelta:
        return self.end_combat.time - self.start_time

    @property
    def player_units(self) -> List[UnitAdded]:
        return [unit for unit in self.begin_combat.active_units if unit.unit_type == "PLAYER"]

    @property
    def pet_units(self) -> List[UnitAdded]:
        return [unit for unit in self.begin_combat.active_units if unit.hostility == "NPC_ALLY"]

    @property
    def is_boss_encounter(self) -> bool:
        return self.begin_combat.is_boss_encounter

    @property
    def boss_units(self) -> Optional[List[UnitAdded]]:
        return self.begin_combat.boss_units

    @property
    def enemy_units(self) -> List[UnitAdded]:
        return self.begin_combat.hostile_units

    def __str__(self):
        return f"{self.__class__.__name__}()"

    __repr__ = __str__