from collections import defaultdict
from typing import List, Dict

from models import EncounterLog, BeginCombat

boss_names = ["Yandir the Butcher", "Captain Vrol", "Lord Falgravn"]


def find_boss_encounters(encounter_log: EncounterLog) -> Dict[str, List[BeginCombat]]:
    boss_encounters = defaultdict(list)
    for boss in boss_names:
        for encounter in encounter_log.combat_encounters:
            units = [unit.name for unit in encounter.extract_enemies()]
            if boss in units:
                boss_encounters[boss].append(encounter)
    return dict(boss_encounters)

