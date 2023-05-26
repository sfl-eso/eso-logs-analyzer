from models import EncounterLog, AbilityUptime
from querying import EventSpan, DebuffSpan


def main():
    """
    https://www.esologs.com/reports/C6GkAg9VKPvYHzrx/
    """
    log = EncounterLog.parse_log("data/markarth_vka.log", multiple=False)
    encounters = log.combat_encounters
    first = encounters[0]
    crusher = log.ability_info_by_name("Crusher")
    span = DebuffSpan(crusher, first, first.end_combat)

    print(f"Inspecting encounter {first}")
    for event in span:
        print(f"Event: {event}")


if __name__ == "__main__":
    main()
