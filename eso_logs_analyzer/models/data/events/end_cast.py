from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .abstract_ability import AbstractAbility
from .enums import CastStatus
from .event import Event

if TYPE_CHECKING:
    from .begin_cast import BeginCast
    from ..encounter_log import EncounterLog


class EndCast(Event, AbstractAbility):
    event_type: str = "END_CAST"

    def __init__(self,
                 id: int,
                 encounter_log: EncounterLog,
                 event_id: int,
                 status: str,
                 cast_effect_id: str,
                 ability_id: str,
                 interrupting_ability_id: str = None,
                 interrupting_unit_id: str = None):
        super(EndCast, self).__init__(id, encounter_log, event_id)
        self.ability_id = int(ability_id)
        self.status: CastStatus = CastStatus(status)
        # Unique id identifying this cast event.
        self.cast_effect_id = int(cast_effect_id)
        self.interrupting_ability_id = int(interrupting_ability_id) if interrupting_ability_id is not None else None
        self.interrupting_unit_id = int(interrupting_unit_id) if interrupting_unit_id is not None else None

        self.begin_casts: List[BeginCast] = []

    @property
    def begin_cast(self) -> Optional[BeginCast]:
        if self.begin_casts:
            return max(self.begin_casts)
        else:
            return None
