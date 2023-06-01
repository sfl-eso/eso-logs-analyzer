from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .abstract_event import AbstractEvent

if TYPE_CHECKING:
    from .ability_info import AbilityInfo


class AbstractAbility(AbstractEvent):
    """
    Provides functionality to get the ability info object for a given ability id.
    Subclasses need to have an instance variable called "ability_id".
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def ability_info(self) -> Optional[AbilityInfo]:
        return self.encounter_log.ability_infos.get(self.ability_id)


class AbstractSynergyAbility(AbstractEvent):
    """
    Provides functionality to get the ability info object for a synergy ability id.
    Subclasses need to have an instance variable called "grants_synergy_ability_id".
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def synergy_ability_info(self) -> Optional[AbilityInfo]:
        return self.encounter_log.ability_infos.get(self.grants_synergy_ability_id)
