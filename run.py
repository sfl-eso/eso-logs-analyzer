from kynes_aegis import find_boss_encounters, YANDIR_THE_BUTCHER, CAPTAIN_VROL, LORD_FALGRAVN
from logger import logger
from models import EncounterLog
from querying import EventSpan, DebuffSpan, print_encounter_stats


def main():
    """
    https://www.esologs.com/reports/C6GkAg9VKPvYHzrx/
    """
    log = EncounterLog.parse_log("/mnt/g/Jan/Projects/ESOLogs/data/markarth_vka.log", multiple=False)
    boss_encounters = find_boss_encounters(log)
    print(f"Evaluating log on {log._begin_log.time}")
    encounter = boss_encounters[YANDIR_THE_BUTCHER][-1]
    print_encounter_stats(encounter, YANDIR_THE_BUTCHER)

    encounter = boss_encounters[CAPTAIN_VROL][-1]
    print_encounter_stats(encounter, CAPTAIN_VROL)

    encounter = boss_encounters[LORD_FALGRAVN][-1]
    print_encounter_stats(encounter, LORD_FALGRAVN)

    # encounters = log.combat_encounters
    # first = encounters[0]
    # crusher_id = 17906
    # crusher = log.ability_info(crusher_id)
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
