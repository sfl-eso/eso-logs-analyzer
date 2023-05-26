from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Tuple, List, Union

from ..base import Base
from ..data import EventSpan
from ..data.events import UnitAdded, CombatEvent, AbilityInfo, Event, EffectChanged
from ..data.events.enums import EffectChangedStatus

if TYPE_CHECKING:
    from .combat_encounter import CombatEncounter


class Unit(Base):

    def __init__(self, combat_encounter: CombatEncounter, unit: UnitAdded):
        super().__init__()
        self.combat_encounter = combat_encounter
        self.unit = unit

        # Compute the "real" time filter for the uptime by finding the first and last combat events targeting the target unit.
        uptime_begin = max(self.unit, self.combat_encounter.begin)
        uptime_end = min(self.unit.unit_removed, self.combat_encounter.end)
        target_uptime = EventSpan(uptime_begin, uptime_end)

        self.uptime_begin_event = self.__compute_new_uptime_boundary(target_uptime)
        self.uptime_end_event = self.__compute_new_uptime_boundary(reversed(target_uptime))
        self.uptime_begin = self.uptime_begin_event.time
        self.uptime_end = self.uptime_end_event.time
        self.logger.debug(f"Shortening uptime begin for {self.display_str} from {uptime_begin.time} to {self.uptime_begin}")
        self.logger.debug(f"Shortening uptime end for {self.display_str} from {uptime_end.time} to {self.uptime_end}")

        # State to compute uptimes more efficiently
        # Contains uptime spans for ability (ability info -> list of span tuples)
        self.__uptime_spans: Dict[AbilityInfo, List[Tuple[EffectChanged, EffectChanged]]] = defaultdict(list)
        # Contains current spans for ability (ability info -> begin event)
        self.__current_span: Dict[AbilityInfo, EffectChanged] = {}
        # Contains current spans for each source unit (ability info -> begin event)
        self.__current_span_per_unit: Dict[AbilityInfo, Dict[UnitAdded, EffectChanged]] = defaultdict(dict)

        self.uptimes_for_abilities: Dict[AbilityInfo, float] = {}
        self.max_uptime_for_abilities: Dict[str, Tuple[AbilityInfo, float]] = {}

    def __compute_new_uptime_boundary(self, iterator) -> CombatEvent:
        """
        Returns the next combat event that targets this uptime's unit.
        """
        for event in iterator:
            if isinstance(event, CombatEvent) and event.target_unit == self.unit:
                return event

    @property
    def duration(self) -> float:
        return (self.uptime_end - self.uptime_begin).total_seconds()

    def uptime_delta(self, event_time: Union[Event, datetime]) -> float:
        if isinstance(event_time, Event):
            event_time = event_time.time
        return (event_time - self.uptime_begin).total_seconds()

    @property
    def display_str(self) -> str:
        return f"{self.unit.name} ({self.unit.unit_id})"

    @property
    def was_killed(self) -> bool:
        return self.uptime_end_event.target_current_health == 0

    def process_effect_changed_event(self, event: EffectChanged):
        if event.target_unit != self.unit:
            return

        # Include effect changed events before combat started (i.e., uptime start event)
        if event < self.unit or event > self.uptime_end_event:
            return

        ability = event.ability_info

        # TODO: record stack counts in EffectChangedStatus.UPDATED events
        # TODO: record uptimes per player for Z'ens

        if event.status == EffectChangedStatus.GAINED:
            if event.unit not in self.__current_span_per_unit[ability]:
                # Only consider the first time an effect is applied for a given unit (multiple sources may apply it)
                self.__current_span_per_unit[ability][event.unit] = event
            if ability not in self.__current_span:
                # Track the first time is applied by any unit
                self.logger.debug(f"Effect {ability.name} ({ability.ability_id}) gained at {self.uptime_delta(event)} for target {self.display_str}")
                # If the event happened before combat started, track the time with the start of combat.
                self.__current_span[ability] = max(event, self.uptime_begin_event)

        elif event.status == EffectChangedStatus.FADED:
            if event.unit in self.__current_span_per_unit[ability]:
                # Remove the start of the span for the current unit
                del self.__current_span_per_unit[ability][event.unit]

                if len(self.__current_span_per_unit[ability]) == 0:
                    # No other units are applying the buff. Record the uptime
                    self.logger.debug(f"Effect {ability.name} ({ability.ability_id}) lost at {self.uptime_delta(event)} for target {self.display_str}")
                    self.__uptime_spans[ability].append((self.__current_span[ability], event))
                    del self.__current_span[ability]

    def compute_debuff_uptimes(self):
        # Close all still open spans for effects that still persist after combat
        for ability in self.__current_span:
            self.__uptime_spans[ability].append((self.__current_span[ability], self.uptime_end_event))

        ability_uptimes: Dict[str, List[Tuple[AbilityInfo, float]]] = defaultdict(list)

        # Compute uptimes for each ability id
        for ability, uptime_spans in self.__uptime_spans.items():
            total_uptime = sum([(faded.time - gained.time).total_seconds() for gained, faded in uptime_spans])
            self.uptimes_for_abilities[ability] = total_uptime
            ability_uptimes[ability.name].append((ability, total_uptime))

        # Compute uptimes for each unique ability name
        for ability_name, uptime_tuples in ability_uptimes.items():
            ability_info, max_uptime = max(uptime_tuples, key=lambda t: t[1])
            self.max_uptime_for_abilities[ability_name] = (ability_info, max_uptime)

    def uptime_for_ability_name(self, ability_name: str) -> float:
        if ability_name not in self.max_uptime_for_abilities:
            self.logger.debug(f"No uptime found for {ability_name} on {self.display_str}")
            return 0.0
        return self.max_uptime_for_abilities[ability_name][1]

    def relative_uptime_for_ability_name(self, ability_name: str) -> float:
        return self.uptime_for_ability_name(ability_name) / self.duration
