from argparse import Namespace
from distutils.dir_util import copy_tree
from pathlib import Path

from python_json_config import Config, ConfigBuilder

from .loading import load_log
from .logging import init_loggers
from .rendering import render_readme, render_log


class Analyzer:
    """
    This class may not inherit from base, since it initializes the loggers with the loaded config.
    This needs to happen before any loggers are instantiated.
    """
    __DEFAULT_CONFIG: str = "config.json"
    __DEFAULT_DEV_CONFIG: str = "config.dev.json"
    __LOG_FILE_SUFFIX: str = ".log"

    def __init__(self, project_root: Path, cli_args: Namespace):
        super().__init__()
        self.project_root = project_root.absolute()
        self.cli_args = cli_args
        self.read_multiple_logs_in_file = cli_args.single

        # Load the specified config file.
        if cli_args.dev:
            config_path = Path(self.__DEFAULT_DEV_CONFIG)
        else:
            config_path = Path(cli_args.config if cli_args.config is not None else self.__DEFAULT_CONFIG)

        if not config_path.is_absolute():
            config_path = self.project_root / config_path

        assert config_path.exists(), f"Config file at {config_path} does not exist."
        self.config: Config = ConfigBuilder().parse_config(str(config_path))

        # Initialize the loggers with the loaded config
        init_loggers(self.config)

        # Ensure the input log file exists
        self.input_dir = Path(cli_args.log)
        assert self.input_dir.exists(), f"Log file or directory at {self.input_dir} does not exist."

    def run(self):
        # Copy the web resources (javascript and css) to target dir.
        copy_tree(str(self.project_root / self.config.web.resource_path), self.config.export.path)

        if self.input_dir.is_file():
            input_files = [self.input_dir]
        else:
            input_files = list([file for file in self.input_dir.iterdir() if file.is_file() and file.suffix == self.__LOG_FILE_SUFFIX])

        for file in input_files:
            logs = load_log(file, self.read_multiple_logs_in_file, self.config)
            render_log(encounter_log=logs, config=self.config, dev_mode=self.cli_args.dev)

        render_readme(self.config, dev_mode=self.cli_args.dev)

        # TODO: trial profiles that can be used/configured via config
        # TODO: gather gear changed events for player before each combat encounter and dynamically check who is using Z'ens to compute its uptime
        # TODO: compute uptimes/infos about boss mechanics (hit/dodge/cleanse of ability)
        # TODO: replace ability and unit ids in str representation by name and ids
        # TODO: theoretical dps gain if we had full uptime
        # TODO: sort abilities by role
        # TODO: group abilities by role (separate tables)?

        # TODO: store metadata for generating of index.html
        # TODO: add table with more metadata in readme (has to be computed when generating logs and stored in metadata)
        # TODO: add navbar and link to github repo to base template (footer) with disclaimer
