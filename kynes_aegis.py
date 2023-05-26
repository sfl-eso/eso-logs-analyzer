from collections import defaultdict
from typing import List, Dict

from models import EncounterLog, BeginCombat

YANDIR_THE_BUTCHER = "Yandir the Butcher"
CAPTAIN_VROL = "Captain Vrol"
LORD_FALGRAVN = "Lord Falgravn"

boss_names = [YANDIR_THE_BUTCHER, CAPTAIN_VROL, LORD_FALGRAVN]


def find_boss_encounters(encounter_log: EncounterLog) -> Dict[str, List[BeginCombat]]:
    boss_encounters = defaultdict(list)
    for boss in boss_names:
        for encounter in encounter_log.combat_encounters:
            if encounter.is_boss_encounter() and boss in [b.name for b in encounter.boss_units]:
                boss_encounters[boss].append(encounter)
    return dict(boss_encounters)

