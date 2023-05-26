from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    from .effect_info import EffectInfo


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
        self.interruptible = interruptible == "T"
        # If true, the ability can be blocked
        self.blockable = blockable == "T"

        # The EffectInfo object belonging to the same ability id
        self.effect_info: EffectInfo = None
