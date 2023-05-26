from argparse import Namespace, ArgumentParser
from pathlib import Path
from typing import Union

from python_json_config import ConfigBuilder, Config

# from loading import EncounterLog
from log import init_loggers
from models.data import EncounterLog


def cli_args() -> Namespace:
    parser = ArgumentParser(prog="ESO Logs Analyzer",
                            description="Analyzes an encounterlog file and computes multiple metrics.")
    parser.add_argument("log", type=str, help="The log file that is analyzed")
    parser.add_argument("--config", default="./config.json", type=str, help="Configuration file (JSON).")
    return parser.parse_args()


def assert_file_exists(path: Union[str, Path]) -> Path:
    path = Path(path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File at {path} does not exist or is not a file!")
    return path


def main(args: Namespace):
    """
    https://www.esologs.com/reports/4VcYzBXARm8wp2yk
    """
    config: Config = ConfigBuilder().parse_config(str(assert_file_exists(args.config)))
    init_loggers(config)
    # TODO: encode data in config?
    # TODO: interactive selection?
    # ability_map = assert_file_exists(config.ability_map)
    log = EncounterLog.parse_log(assert_file_exists(args.log), multiple=False)

    # encounters: List[Encounter] = [Encounter(begin_combat) for begin_combat in
    #                                tqdm(log.combat_encounters, desc="Processing encounters")]
    # for encounter in encounters:
    #     print(encounter)

    # boss_encounters = find_boss_encounters(log)
    # print(f"Evaluating log on {log._begin_log.time}")
    # all_uptimes = {}
    # for boss in [YANDIR_THE_BUTCHER, CAPTAIN_VROL, LORD_FALGRAVN]:
    #     encounter = boss_encounters[boss][-1]
    #     boss_unit = encounter.get_hostile_unit(boss)
    #     uptimes = debuffs_target_unit(log, encounter, ability_file, boss_unit)
    #     all_uptimes[encounter] = uptimes
    # all_uptimes

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
    main(cli_args())
