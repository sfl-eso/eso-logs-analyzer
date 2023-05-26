from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    from .begin_combat import BeginCombat


class EndCombat(Event):
    event_type: str = "END_COMBAT"

    def __init__(self, id: int):
        super(EndCombat, self).__init__(id)
        self.begin_combat: BeginCombat = None