from __future__ import annotations

from typing import TYPE_CHECKING

from .combat_event import CombatEvent

if TYPE_CHECKING:
    pass


class SoulGemResurrectionAcceptedEvent(CombatEvent):
    """
    Filler class for events of players accepting soul gem resurrections.
    The ability id will be 0 and have no matching info event.
    """
    # TODO: this is class required? How else could this be documented?
    pass
