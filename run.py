from argparse import Namespace, ArgumentParser
from distutils.dir_util import copy_tree
from pathlib import Path
from typing import Union

from python_json_config import ConfigBuilder, Config

from log import init_loggers
from models.data import EncounterLog
from rendering import render_log, render_readme


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

    # Copy the web resources (javascript and css) to target dir.
    copy_tree(config.web.resource_path, config.export.path)

    logs: EncounterLog = EncounterLog.parse_log(assert_file_exists(args.log), multiple=True)
    render_log(logs, config)
    render_readme(config)

    # TODO: trial profiles that can be used/configured via config
    # TODO: gather gear changed events for player before each combat encounter and dynamically check who is using Z'ens to compute its uptime
    # TODO: compute uptimes/infos about boss mechanics (hit/dodge/cleanse of ability)
    # TODO: replace ability and unit ids in str representation by name and ids
    # TODO: theoretical dps gain if we had full uptime
    # TODO: sort abilities by role
    # TODO: group abilities by role (separate tables)?
    # TODO: auto collapse encounters and mark the boss hp % when we died (or cleared the encounter)

    # TODO: store metadata for generating of index.html


if __name__ == "__main__":
    main(cli_args())
