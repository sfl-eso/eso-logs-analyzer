from __future__ import annotations

from typing import List, TYPE_CHECKING, Dict

from decorators import requires_load, requires_target
from loading import UnitAdded, TargetEvent, HealthRegen, CombatEvent, AbilityInfo
from .data_processor import DataProcessor

if TYPE_CHECKING:
    from .encounter import Encounter


class EncounterPlayer(DataProcessor):
    def __init__(self, encounter: Encounter, unit: UnitAdded):
        super().__init__()

        assert unit.unit_type == "PLAYER", f"Unit {unit} is not a player!"
        self.encounter = encounter
        self.unit = unit

        # Load data for this encounter
        self.pets: List[UnitAdded] = self.unit.pets[encounter.begin_combat]
        self.combat_events_source: List[TargetEvent] = self.unit.combat_events_source[encounter.begin_combat]
        self.combat_events_target: List[TargetEvent] = self.unit.combat_events_target[encounter.begin_combat]
        self.health_regen_events: List[HealthRegen] = self.unit.health_regen_events[encounter.begin_combat]

        self.damage_event_dict: Dict[UnitAdded, List[CombatEvent]] = {}

    def __str__(self):
        return f"{self.__class__.__name__}(account={self.unit.account}, encounter={self.encounter})"

    __repr__ = __str__

    def load(self):
        if not self._loaded:
            self.load_damage_events()
            self._loaded = True

    def _load_damage_events_to_target(self, target: UnitAdded):
        player_damage_events: List[CombatEvent] = [event for event in self.combat_events_source
                                                   if event.filter_by_type_and_target(CombatEvent, target)]

        pet_damage_events: List[CombatEvent] = []
        for pet in self.pets:
            pet_events: List[CombatEvent] = [event for event in pet.combat_events_source[self.encounter.begin_combat]
                                             if event.filter_by_type_and_target(CombatEvent, target)]
            pet_damage_events.extend(pet_events)

        self.damage_event_dict[target] = player_damage_events + pet_damage_events

    def load_damage_events(self):
        for target in self.encounter.enemy_units:
            self._load_damage_events_to_target(target)

    @requires_load
    def dps(self):
        total_damage = 0
        for target_damage_events in self.damage_event_dict.values():
            total_damage += sum([event.damage for event in target_damage_events])
        return total_damage / self.encounter.duration.total_seconds()

    @requires_load
    def dps_by_ability(self, ability: AbilityInfo):
        total_damage = 0
        for target_damage_events in self.damage_event_dict.values():
            total_damage += sum([event.damage for event in target_damage_events if event.ability == ability])
        return total_damage / self.encounter.duration.total_seconds()

    @requires_load
    @requires_target
    def dps_to_target(self, target: UnitAdded):
        total_damage = sum([event.damage for event in self.damage_event_dict[target]])
        return total_damage / self.encounter.duration.total_seconds()

    @requires_load
    @requires_target
    def dps_to_target_by_ability(self, target: UnitAdded, ability: AbilityInfo):
        total_damage = sum([event.damage for event in self.damage_event_dict[target] if event.ability == ability])
        return total_damage / self.encounter.duration.total_seconds()
