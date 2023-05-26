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
    parser.add_argument("log", type=str, help="The log file that is analyzed or a directory containing multiple log files")
    parser.add_argument("--config", default="./config.json", type=str, help="Configuration file (JSON).")
    return parser.parse_args()


def assert_file_exists(path: Union[str, Path], assert_file: bool = True) -> Path:
    path = Path(path)
    if not path.exists() or (assert_file and not path.is_file()):
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

    input_files = []
    log_input = assert_file_exists(args.log, assert_file=False)
    if log_input.is_file():
        input_files = [log_input]
    else:
        for file in log_input.iterdir():
            if file.is_file() and file.suffix == ".log":
                input_files.append(file)

    print(f"Processing {len(input_files)} log files...")
    for log_file in input_files:
        logs = EncounterLog.parse_log(log_file, multiple=True)
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
    # TODO: add table with more metadata in readme (has to be computed when generating logs and stored in metadata)
    # TODO: add navbar and link to github repo to base template (footer) with disclaimer


if __name__ == "__main__":
    main(cli_args())
