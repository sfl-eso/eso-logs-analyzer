from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import CastStatus
from .event import Event

if TYPE_CHECKING:
    from .begin_cast import BeginCast
    from .ability_info import AbilityInfo
    from ..encounter_log import EncounterLog


class EndCast(Event):
    event_type: str = "END_CAST"

    def __init__(self, id: int, status: str, cast_effect_id, ability_id, interrupting_ability_id: str = None,
                 interrupting_unit_id: str = None):
        super(EndCast, self).__init__(id)
        self.ability_id = int(ability_id)
        self.status: CastStatus = CastStatus(status)
        self.cast_effect_id = int(cast_effect_id)
        self.interrupting_ability_id = int(interrupting_ability_id) if interrupting_ability_id is not None else None
        self.interrupting_unit_id = int(interrupting_unit_id) if interrupting_unit_id is not None else None

        self.begin_cast: BeginCast = None
        self.ability_info: AbilityInfo = None

    def resolve_ability_and_effect_info_references(self, encounter_log: EncounterLog):
        self.ability_info = encounter_log.ability_infos.get(self.ability_id)
