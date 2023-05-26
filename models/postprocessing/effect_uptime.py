from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import Base
from ..data.events import AbilityInfo, UnitAdded

if TYPE_CHECKING:
    from .combat_encounter import CombatEncounter


class EffectUptime(Base):
    def __init__(self, combat_encounter: CombatEncounter, target_unit: UnitAdded, ability_info: AbilityInfo):
        super().__init__()
        self.combat_encounter = combat_encounter
        self.target_unit = target_unit
        self.ability_info = ability_info
