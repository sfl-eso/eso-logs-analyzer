from kynes_aegis import find_boss_encounters, YANDIR_THE_BUTCHER
from logger import logger
from models import EncounterLog
from querying import EventSpan, DebuffSpan


def main():
    """
    https://www.esologs.com/reports/C6GkAg9VKPvYHzrx/
    """
    log = EncounterLog.parse_log("/mnt/g/Jan/Projects/ESOLogs/data/markarth_vka.log", multiple=False)
    # for encounter in log.combat_encounters:
    #     print(f"Enemies in encounter {encounter}")
    #     units = sorted(set([unit.name for unit in encounter.hostile_units]))
    #     for enemy in units:
    #         print(enemy)
    #     print()
    boss_encounters = find_boss_encounters(log)
    encounter = boss_encounters[YANDIR_THE_BUTCHER][0]
    unit = encounter.active_units[0]
    yandir = [unit for unit in encounter.hostile_units if unit.name == YANDIR_THE_BUTCHER][0]
    damage = unit.damage_done(encounter, yandir)
    encounter
    print(boss_encounters)

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
