from argparse import Namespace, ArgumentParser
from pathlib import Path

from eso_logs_analyzer import Analyzer


def cli_args() -> Namespace:
    parser = ArgumentParser(prog="ESO Logs Analyzer",
                            description="Analyzes an encounterlog file and computes multiple metrics.")
    parser.add_argument("log", type=str, help="The log file that is analyzed or a directory containing multiple log files")
    parser.add_argument("--config", default="./config.json", type=str, help="Configuration file (JSON).")
    parser.add_argument("--dev", action="store_true", help="Set to enable development mode (i.e. use dev config and load css from web).")
    parser.add_argument("--single", action="store_false", help="Set to only read the first encounterlog in each log file.")
    return parser.parse_args()


def main(args: Namespace):
    analyzer = Analyzer(project_root=Path(__file__).parent, cli_args=args)
    analyzer.run()


if __name__ == "__main__":
    main(cli_args())
