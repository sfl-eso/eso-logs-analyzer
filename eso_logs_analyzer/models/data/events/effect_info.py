from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import EffectType, StatusEffectType, NoEffectBar
from .event import Event

if TYPE_CHECKING:
    from .ability_info import AbilityInfo
    from ..encounter_log import EncounterLog


class EffectInfo(Event):
    event_type: str = "EFFECT_INFO"

    def __init__(self,
                 id: int,
                 encounter_log: EncounterLog,
                 event_id: int,
                 ability_id: str,
                 effect_type: str,
                 status_effect_type: str,
                 no_effect_bar: str,
                 grants_synergy_ability_id: str = None):
        super(EffectInfo, self).__init__(id, encounter_log, event_id)
        # Id of the ability (same as ingame)
        self.ability_id = int(ability_id)
        # What kind of effect this is (i.e., buff, debuff)
        self.effect_type: EffectType = EffectType(effect_type)
        # The type of status effect if one is applied by this effect
        self.status_effect_type: StatusEffectType = StatusEffectType(status_effect_type)
        # TODO: what does this mean?
        self.no_effect_bar: NoEffectBar = NoEffectBar(no_effect_bar)
        # If set, this ability id is the synergy granted by this effect
        self.grants_synergy_ability_id = int(grants_synergy_ability_id) if grants_synergy_ability_id is not None else None

        # The AbilityInfo object belonging to the same ability id
        self.ability_info: AbilityInfo = None
        self.synergy_ability_info: AbilityInfo = None

    def resolve_ability_and_effect_info_references(self, encounter_log: EncounterLog):
        self.ability_info = encounter_log.ability_infos.get(self.ability_id)
        self.synergy_ability_info = encounter_log.ability_infos.get(self.grants_synergy_ability_id)
