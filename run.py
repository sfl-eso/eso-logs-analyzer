from pathlib import Path

from kynes_aegis import find_boss_encounters, YANDIR_THE_BUTCHER, CAPTAIN_VROL, LORD_FALGRAVN
from logger import logger
from models import EncounterLog
from querying import EventSpan, EffectSpan, print_encounter_stats, debuffs_target_unit


def main():
    """
    https://www.esologs.com/reports/C6GkAg9VKPvYHzrx/
    """
    log = EncounterLog.parse_log("/mnt/g/Jan/Projects/ESOLogs/data/markarth_vka.log", multiple=False)
    ability_file = Path("/mnt/g/Jan/Projects/ESOLogs/ability_map.json")
    boss_encounters = find_boss_encounters(log)
    print(f"Evaluating log on {log._begin_log.time}")
    all_uptimes = {}
    for boss in [YANDIR_THE_BUTCHER, CAPTAIN_VROL, LORD_FALGRAVN]:
        encounter = boss_encounters[boss][-1]
        boss_unit = encounter.get_hostile_unit(boss)
        uptimes = debuffs_target_unit(log, encounter, ability_file, boss_unit)
        all_uptimes[encounter] = uptimes
    all_uptimes

    # print_encounter_stats(encounter, YANDIR_THE_BUTCHER)
    #
    # encounter = boss_encounters[CAPTAIN_VROL][-1]
    # print_encounter_stats(encounter, CAPTAIN_VROL)
    #
    # encounter = boss_encounters[LORD_FALGRAVN][-1]
    # print_encounter_stats(encounter, LORD_FALGRAVN)

    # encounters = log.combat_encounters
    # first = encounters[0]

    # span = DebuffSpan(crusher, first, first.end_combat)
    # unit_dict = span.debuff_by_units()
    # logger().info(f"Inspecting encounter {first}")
    # for unit, events in unit_dict.items():
    #     logger().info(f"Unit: {unit} has events")
    #     for event in events:
    #         logger().info(event)
    #     print()


if __name__ == "__main__":
    main()
