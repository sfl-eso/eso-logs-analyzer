from argparse import Namespace, ArgumentParser
from pathlib import Path
from typing import Union

from python_json_config import ConfigBuilder, Config

from export import generate_markdown_file
from log import init_loggers
from models.data import EncounterLog
from models.postprocessing import CombatEncounter
from models.postprocessing.effect_uptime import EffectUptime


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


def print_uptime(effect_uptime: EffectUptime):
    ability, uptime, total_time = effect_uptime.compute_uptime()
    relative_uptime = round(uptime / total_time, 4)

    encounter_begin = effect_uptime.combat_encounter.begin.time
    target_spawn = (effect_uptime.uptime_begin - encounter_begin).total_seconds()
    target_death = (effect_uptime.uptime_end - encounter_begin).total_seconds()
    target_uptime = f"from {round(target_spawn, 2)}s to {round(target_death, 2)}s"

    message = ""
    message += f"Uptime for {ability.name} ({ability.ability_id}) "
    message += f"on {effect_uptime.target_unit.name} ({effect_uptime.target_unit.unit_id}): {relative_uptime} "
    message += f"(uptime: {round(uptime, 4)}, target_uptime: {target_uptime})"
    print(message)


def main(args: Namespace):
    """
    https://www.esologs.com/reports/4VcYzBXARm8wp2yk
    """
    config: Config = ConfigBuilder().parse_config(str(assert_file_exists(args.config)))
    init_loggers(config)

    log: EncounterLog = EncounterLog.parse_log(assert_file_exists(args.log), multiple=False)
    combat_encounters = CombatEncounter.load(log)
    generate_markdown_file(config, log, combat_encounters)

    # TODO: trial profiles that can be used/configured via config
    # TODO: compute uptimes using callbacks on objects to reduce number of times events are iterated
    # TODO: gather gear changed events for player before each combat encounter and dynamically check who is using Z'ens to compute its uptime
    # TODO: compute uptimes/infos about boss mechanics (hit/dodge/cleanse of ability)
    # TODO: replace ability and unit ids in str representation by name and ids
    # TODO: theoretical dps gain if we had full uptime
    # TODO: sort abilities by role
    # TODO: group abilities by role (separate tables)?
    # TODO: auto collapse encounters and mark the boss hp % when we died (or cleared the encounter)


if __name__ == "__main__":
    main(cli_args())
