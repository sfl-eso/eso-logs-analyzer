import json
from collections import defaultdict
from pathlib import Path
from typing import Dict

from loading import BeginCombat, UnitAdded, EncounterLog

from .effect_span import EffectUnitSpan


def debuffs_target_unit(log: EncounterLog, encounter: BeginCombat, ability_file: Path, target_unit: UnitAdded) -> Dict[str, EffectUnitSpan]:
    ability_dict = json.load(open(ability_file))
    uptimes_by_ability_name = defaultdict(list)
    for ability_id, name in ability_dict["debuffs"].items():
        try:
            ability = log.ability_info(ability_id)
        except KeyError:
            # The effect did not appear in the encounter
            # TODO: create a 0 uptime class
            continue
        effect_span = EffectUnitSpan(ability=ability, start=encounter, end=encounter.end_combat, target_unit=target_unit)
        uptimes_by_ability_name[name].append(effect_span)

    ability_uptimes = {}
    for name, uptimes in uptimes_by_ability_name.items():
        # Nothing to merge
        if len(uptimes) == 1:
            ability_uptimes[name] = uptimes[0]
        else:
            merged_uptime = uptimes[0]
            for uptime in uptimes[1:]:
                merged_uptime = EffectUnitSpan.merge(merged_uptime, uptime)
            ability_uptimes[name] = merged_uptime
    return ability_uptimes
