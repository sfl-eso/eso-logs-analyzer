from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict

from loading import EndCombat
from ..base import Base
from ..data import EncounterLog, EventSpan
from ..data.events import BeginCombat, UnitAdded, UnitRemoved
from ..data.events.enums import Hostility

if TYPE_CHECKING:
    pass


class CombatEncounter(Base):
    def __init__(self, event_span: EventSpan):
        super().__init__()
        self.event_span = event_span

    def __str__(self):
        return f"{self.__class__.__name__}(start={self.event_span.start.time}, end={self.event_span.end.time}, duration={self.event_span.duration})"

    @classmethod
    def load(cls, encounter_log: EncounterLog) -> List[CombatEncounter]:
        encounters = []

        hostile_units: Dict[int, UnitAdded] = {}

        for event in encounter_log.events:
            if isinstance(event, UnitAdded) and event.hostility == Hostility.HOSTILE:
                assert event.unit_id not in hostile_units, f"New unit with id {event.unit_id} exists already"
                hostile_units[event.unit_id] = event
                cls.event_logger.info((event, f"\tAdding new hostile unit {event}"))
            elif isinstance(event, UnitRemoved) and event.unit_added.hostility == Hostility.HOSTILE:
                assert event.unit_id in hostile_units, f"Unit with id {event.unit_id} is removed but does not exist"
                cls.event_logger.info((event, f"\tRemoving hostile unit {event}"))
                del hostile_units[event.unit_id]

                if len(hostile_units) == 0:
                    cls.event_logger.info((event, f"### NO HOSTILE UNITS LEFT ###"))

            elif isinstance(event, BeginCombat):
                cls.event_logger.info((event, f"Entering combat {event}"))
            elif isinstance(event, EndCombat):
                cls.event_logger.info((event, f"Leaving combat {event} (begin combat {event.begin_combat})"))

        # begin_combat_events: List[BeginCombat] = encounter_log.events_for_type(BeginCombat)
        #
        # for begin_combat_event in begin_combat_events:
        #     encounters.append(CombatEncounter(begin_combat_event.span_to_end))

        return encounters
