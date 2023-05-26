from datetime import datetime, timedelta
from typing import List, Optional

from decorators import requires_load, requires_target
from loading import BeginCombat, UnitAdded, AbilityInfo
from .data_processor import DataProcessor
from .encounter_player import EncounterPlayer


class Encounter(DataProcessor):
    def __init__(self, begin_combat: BeginCombat):
        super().__init__()
        self.begin_combat = begin_combat
        self.end_combat = self.begin_combat.end_combat
        self.start_time: datetime = self.begin_combat.time
        self.duration: timedelta = self.end_combat.time - self.start_time

        self.is_boss_encounter: bool = self.begin_combat.is_boss_encounter
        self.boss_units: Optional[List[UnitAdded]] = self.begin_combat.boss_units
        self.enemy_units: List[UnitAdded] = self.begin_combat.hostile_units
        self.pet_units: List[UnitAdded] = [unit for unit in self.begin_combat.active_units if
                                           unit.hostility == "NPC_ALLY"]

        self.players: List[EncounterPlayer] = [EncounterPlayer(self, unit) for unit in self.begin_combat.active_units
                                               if unit.unit_type == "PLAYER"]
        self.load()

    def load(self):
        if not self._loaded:
            for player in self.players:
                player.load()
            self._loaded = True

    @property
    def name(self):
        if self.is_boss_encounter:
            # TODO: boss/encounter name
            return ",".join([unit.name for unit in self.boss_units])
        else:
            return "Trash"

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name}, start={self.start_time}, duration={self.duration})"

    __repr__ = __str__

    @requires_load
    def dps(self):
        return sum([player.dps() for player in self.players])

    @requires_load
    def dps_by_ability(self, ability: AbilityInfo):
        return sum([player.dps_by_ability(ability) for player in self.players])

    @requires_load
    @requires_target
    def dps_to_target(self, target: UnitAdded):
        return sum([player.dps_to_target(target) for player in self.players])
