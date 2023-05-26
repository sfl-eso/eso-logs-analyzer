from collections import defaultdict
from typing import List, Dict

from loading import EncounterLog, BeginCombat

OAXILTSO = "Oaxiltso"
FLAME_HERALD_BAHSEI = "Flame-Herald Bahsei"
XALVAKKA = "Xalvakka"

boss_names = [OAXILTSO, FLAME_HERALD_BAHSEI, XALVAKKA]


def find_boss_encounters(encounter_log: EncounterLog) -> Dict[str, List[BeginCombat]]:
    boss_encounters = defaultdict(list)
    for boss in boss_names:
        for encounter in encounter_log.combat_encounters:
            if encounter.is_boss_encounter and boss in [b.name for b in encounter.boss_units]:
                boss_encounters[boss].append(encounter)
    return dict(boss_encounters)

