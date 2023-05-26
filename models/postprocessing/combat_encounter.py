from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, List, Dict

from trials import get_boss_for_trial
from ..base import Base
from ..data import EncounterLog, EventSpan
from ..data.events import UnitAdded, EndCombat, BeginCombat, Event, CombatEvent, UnitChanged
from ..data.events.enums import Hostility

if TYPE_CHECKING:
    pass


class CombatEncounter(Base):
    DEFAULT_NAME: str = "Trash"

    def __init__(self, begin: BeginCombat, end: Event):
        super().__init__()
        self.__begin = begin
        self.__end = end
        self.event_span = EventSpan(self.__begin, self.__end)
        # TODO: determine until when the encounter can go (at most up to the next begin combat)
        # TODO: split the events into buckets by a unit (e.g., a second) and determine dps to units during those buckets to determine the second until combat is going
        # TODO: determine the last damage event to enemies

        self.hostile_units = self.load_hostile_units()
        self.boss_units = [unit for unit in self.hostile_units if unit.is_boss]
        self.trialId = self.__begin.begin_trial.trial_id

    def __str__(self):
        name = self.get_boss().value if self.is_boss_encounter else self.DEFAULT_NAME
        return f"{self.__class__.__name__}(name={name}, start={self.event_span.start.time}, end={self.event_span.end.time}, duration={self.event_span.duration})"

    __repr__ = __str__

    @property
    def is_boss_encounter(self) -> bool:
        return len(self.boss_units) > 0

    def get_boss(self):
        return get_boss_for_trial(self.trialId, self.boss_units)

    def load_hostile_units(self) -> List[UnitAdded]:
        """
        Load every hostile unit that was damaged during this encounter. This filters any units that are only there for mechanics (such as HM mechanics)
        """
        active_units: Dict[UnitAdded, bool] = {}
        for event in self.event_span:
            if isinstance(event, UnitAdded) and event.hostility == Hostility.HOSTILE:
                if event not in active_units:
                    active_units[event] = False
            elif isinstance(event, UnitChanged) and event.hostility == Hostility.HOSTILE:
                if event not in active_units:
                    active_units[event.unit_added] = False
            elif isinstance(event, CombatEvent) and event.target_unit is not None and event.target_unit.hostility == Hostility.HOSTILE:
                active_units[event.target_unit] = True

        return [unit for unit, was_damaged in active_units.items() if was_damaged]

    @classmethod
    def load(cls, encounter_log: EncounterLog) -> List[CombatEncounter]:
        encounters = []
        begin_encounter: BeginCombat = None
        last_end_combat: EndCombat = None
        # The time difference between an end combat and begin combat event needs to be larger than this delta for them to be considered different
        # combat encounters.
        combat_phase_delta: timedelta = timedelta(seconds=2)

        for event in encounter_log.events:
            if isinstance(event, BeginCombat):
                if begin_encounter is None:
                    begin_encounter = event
                elif last_end_combat is not None and (event.time - last_end_combat.time) < combat_phase_delta:
                    # The time delta between this begin combat and the last end combat is too small.
                    # The encounter is still ongoing
                    continue
                else:
                    # This is a new encounter. We can save the data for the last encounter.
                    encounters.append(CombatEncounter(begin_encounter, last_end_combat))

                    # Reset the variables determining the combat encounters
                    begin_encounter = event
                    last_end_combat = None
            elif isinstance(event, EndCombat):
                last_end_combat = event

        if begin_encounter is not None and last_end_combat is not None:
            # Create the last encounter
            encounter = CombatEncounter(begin_encounter, last_end_combat)
            encounters.append(encounter)

        return encounters
