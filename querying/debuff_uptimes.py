from collections import defaultdict
from datetime import timedelta
from typing import List

from models import BeginCombat, AbilityInfo, UnitAdded, EffectChanged

from .effect_span import EffectSpan, EffectUnitSpan


def debuff_target_unit(encounter: BeginCombat, ability: AbilityInfo, target_unit: UnitAdded) -> dict:
    span = EffectUnitSpan(ability=ability, start=encounter, end=encounter.end_combat, target_unit=target_unit)
    uptimes = span._uptime_spans()

    total_combat_time = encounter.end_combat.time - encounter.time
    total_debuff_time = sum([span.duration().total_seconds() for span in uptimes])

    return {
        "unit": target_unit,
        "ability": ability,
        "combat_time": total_combat_time,
        "debuff_time": total_debuff_time
    }
