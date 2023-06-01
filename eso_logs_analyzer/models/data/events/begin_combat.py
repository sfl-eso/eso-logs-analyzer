from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event
from .span_event import SpanCast

if TYPE_CHECKING:
    from .end_combat import EndCombat
    from .trial_init import TrialInit
    from ..encounter_log import EncounterLog


class BeginCombat(SpanCast):
    event_type: str = "BEGIN_COMBAT"

    def __init__(self, id: int, encounter_log: EncounterLog, event_id: int):
        super(BeginCombat, self).__init__(id, encounter_log, event_id)
        # The corresponding end combat event
        self.end_combat: EndCombat = None
        self.trial_init: TrialInit = None

    @property
    def end_event(self) -> Event:
        return self.end_combat

    @end_event.setter
    def end_event(self, value: Event):
        self.end_combat = value
