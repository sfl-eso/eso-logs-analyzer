from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import CastStatus
from .event import Event

if TYPE_CHECKING:
    from .begin_cast import BeginCast


class EndCast(Event):
    event_type: str = "END_CAST"

    def __init__(self, id: int, status: str, cast_effect_id, ability_id, interrupting_ability_id: str = None,
                 interrupting_unit_id: str = None):
        super(EndCast, self).__init__(id)
        self.ability_id = int(ability_id)
        self.status: CastStatus = CastStatus(status)
        self.cast_effect_id = int(cast_effect_id)
        self.interrupting_ability_id = int(interrupting_ability_id)
        self.interrupting_unit_id = int(interrupting_unit_id)

        self.begin_cast: BeginCast = None
