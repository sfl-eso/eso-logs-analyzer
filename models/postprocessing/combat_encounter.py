from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, List, Dict

from ..base import Base
from ..data import EncounterLog, EventSpan
from ..data.events import UnitAdded, EndCombat, BeginCombat, Event

if TYPE_CHECKING:
    pass


class CombatEncounter(Base):
    def __init__(self, begin: BeginCombat, end: EndCombat):
        super().__init__()
        self.event_span = EventSpan(begin, end)
        # TODO: determine until when the encounter can go (at most up to the next begin combat)
        # TODO: split the events into buckets by a unit (e.g., a second) and determine dps to units during those buckets to determine the second until combat is going
        # TODO: determine the last damage event to enemies

    def __str__(self):
        return f"{self.__class__.__name__}(start={self.event_span.start.time}, end={self.event_span.end.time}, duration={self.event_span.duration})"

    @classmethod
    def __extend_encounter(cls, start: Event, end: Event):
        pass

    @classmethod
    def load(cls, encounter_log: EncounterLog) -> List[CombatEncounter]:
        encounters = []

        hostile_units: Dict[int, UnitAdded] = {}

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
                    encounter = CombatEncounter(begin_encounter, last_end_combat)
                    encounters.append(encounter)

                    # Reset the variables determining the combat encounters
                    begin_encounter = event
                    last_end_combat = None
            elif isinstance(event, EndCombat):
                last_end_combat = event

            # if isinstance(event, UnitAdded) and event.hostility == Hostility.HOSTILE:
            #     assert event.unit_id not in hostile_units, f"New unit with id {event.unit_id} exists already"
            #     hostile_units[event.unit_id] = event
            #     cls.event_logger.info((event, f"\tAdding new hostile unit {event}"))
            # elif isinstance(event, UnitRemoved) and event.unit_added.hostility == Hostility.HOSTILE:
            #     assert event.unit_id in hostile_units, f"Unit with id {event.unit_id} is removed but does not exist"
            #     cls.event_logger.info((event, f"\tRemoving hostile unit {event}"))
            #     del hostile_units[event.unit_id]
            #
            #     if len(hostile_units) == 0:
            #         cls.event_logger.info((event, f"### NO HOSTILE UNITS LEFT ###"))
            #
            # elif isinstance(event, BeginCombat):
            #     cls.event_logger.info((event, f"Entering combat {event}"))
            # elif isinstance(event, EndCombat):
            #     cls.event_logger.info((event, f"Leaving combat {event} (begin combat {event.begin_combat})"))

        if begin_encounter is not None and last_end_combat is not None:
            # Create the last encounter
            encounter = CombatEncounter(begin_encounter, last_end_combat)
            encounters.append(encounter)

        return encounters
