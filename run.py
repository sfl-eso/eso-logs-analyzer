from kynes_aegis import find_boss_encounters
from logger import logger
from models import EncounterLog
from querying import EventSpan, DebuffSpan


def main():
    """
    https://www.esologs.com/reports/C6GkAg9VKPvYHzrx/
    """
    log = EncounterLog.parse_log("data/markarth_vka.log", multiple=False)
    boss_encounters = find_boss_encounters(log)
    boss_encounters

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
