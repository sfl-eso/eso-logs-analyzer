from __future__ import annotations

from typing import TYPE_CHECKING, List

from .event import Event

if TYPE_CHECKING:
    from .end_combat import EndCombat
    from .unit_added import UnitAdded


class BeginCombat(Event):
    event_type: str = "BEGIN_COMBAT"

    def __init__(self, id: int):
        super(BeginCombat, self).__init__(id)
        # The corresponding end combat event
        self.end_combat: EndCombat = None

        # TODO: are these necessary?
        self.events: List[Event] = []

        # Units that are alive/active as the encounter starts
        self.start_units: List[UnitAdded] = []
        # Units that are alive/active during the encounter
        self.active_units: List[UnitAdded] = []
        # Units that are alive/active as the encounter ends
        self.end_units: List[UnitAdded] = []
        # All enemy units that appear during the encounter
        self.hostile_units: List[UnitAdded] = []

        self.buff_events: list = []
        self.debuff_events: list = []
        self.debuff_taken_events: list = []
        self.damage_done_events: list = []
        self.damage_taken_events: list = []
