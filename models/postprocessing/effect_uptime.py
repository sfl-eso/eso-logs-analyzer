from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple, Optional

from ..base import Base
from ..data import EventSpan
from ..data.events import AbilityInfo, UnitAdded, EffectChanged
from ..data.events.enums import EffectChangedStatus

if TYPE_CHECKING:
    from .combat_encounter import CombatEncounter


class EffectUptime(Base):
    def __init__(self, combat_encounter: CombatEncounter, target_unit: UnitAdded, ability_name: str):
        super().__init__()
        self.combat_encounter = combat_encounter
        self.target_unit = target_unit

        self.uptime_begin = max(self.target_unit.time, self.combat_encounter.begin.time)
        self.uptime_end = min(self.target_unit.unit_removed.time, self.combat_encounter.end.time)

        self.ability_infos = [ability for ability in self.combat_encounter.encounter_log.ability_infos.values() if ability.name == ability_name]
        if len(self.ability_infos) == 0:
            self.logger.error(f"No ability with name '{ability_name}' found. Can't compute uptime!")

    def __compute_uptime(self, ability_info: AbilityInfo) -> float:
        """
        Uptimes are recorded per unit and the effect changed events only specify the effect status for a unit.
        """
        # Also include events before combat started. Some effects can be applied out of combat
        effect_events: List[EffectChanged] = [event for event in EventSpan(self.target_unit, self.combat_encounter.end)
                                              if isinstance(event, EffectChanged) and event.target_unit == self.target_unit and event.ability_info == ability_info]
        uptime_spans = []
        current_span_per_unit = {}
        current_span = None
        for event in effect_events:
            if event.status == EffectChangedStatus.GAINED:
                if event.unit not in current_span_per_unit:
                    # Only consider the first time an effect is applied for a given unit (multiple sources may apply it)
                    current_span_per_unit[event.unit] = event
                if current_span is None:
                    # Track the first time is applied by any unit
                    self.logger.debug(f"Effect {ability_info.name} ({ability_info.ability_id}) gained at {(event.time - self.uptime_begin).total_seconds()} "
                                      f"for target {self.target_unit.name} ({self.target_unit.unit_id})")
                    # If the event happened before combat started, track the time with the start of combat.
                    current_span = max(event, self.combat_encounter.begin)

            elif event.status == EffectChangedStatus.FADED:
                if event.unit in current_span_per_unit:
                    # Remove the start of the span for the current unit
                    del current_span_per_unit[event.unit]

                    if len(current_span_per_unit) == 0:
                        # No other units are applying the buff. Record the uptime
                        self.logger.debug(
                            f"Effect {ability_info.name} ({ability_info.ability_id}) lost at {(event.time - self.uptime_begin).total_seconds()} "
                            f"for target {self.target_unit.name} ({self.target_unit.unit_id})")
                        uptime_spans.append((current_span, event))
                        current_span = None

        if current_span is not None:
            # The effect still persist after combat. In this case append a final span with the end of combat as end time.
            uptime_spans.append((current_span, self.combat_encounter.end))

        total_uptime = sum([(faded.time - gained.time).total_seconds() for gained, faded in uptime_spans])
        return total_uptime

    def compute_uptime(self) -> Optional[Tuple[AbilityInfo, float, float]]:
        uptimes = [(ability, self.__compute_uptime(ability)) for ability in self.ability_infos]
        if uptimes:
            max_uptime_ability, max_uptime = max(uptimes, key=lambda t: t[1])
            total_target_uptime = self.uptime_end - self.uptime_begin
            return max_uptime_ability, max_uptime, total_target_uptime.total_seconds()
