from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    from .effect_info import EffectInfo
    from ..encounter_log import EncounterLog


class AbilityInfo(Event):
    event_type: str = "ABILITY_INFO"

    def __init__(self, id: int, ability_id: str, name: str, icon_path: str, interruptible: str, blockable: str):
        super(AbilityInfo, self).__init__(id)
        # Id of the ability (same as ingame)
        self.ability_id = int(ability_id)
        # Name of the ability (i.e., Major Prophecy)
        self.name = name
        # Path to the icon file in the game files
        self.icon_path = icon_path
        # If true, the ability can be interrupted
        self.interruptible = self._convert_boolean(interruptible, field_name="interruptible")
        # If true, the ability can be blocked
        self.blockable = self._convert_boolean(blockable, field_name="blockable")

        # The EffectInfo object belonging to the same ability id
        self.effect_info: EffectInfo = None

    def resolve_ability_and_effect_info_references(self, encounter_log: EncounterLog):
        self.effect_info = encounter_log.effect_infos.get(self.ability_id)
