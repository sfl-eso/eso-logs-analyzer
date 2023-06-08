from pathlib import Path
from typing import Union

from python_json_config import Config

from .log_loader import LogLoader
from .parallel_loader import ParallelLoader


def load_log(file: Union[str, Path], multiple: bool, config: Config):
    if config.parallel is not None and config.parallel.num_processes > 1:
        loader_class = ParallelLoader
        loader_kwargs = dict(num_processes=config.parallel.num_processes, num_chunks=config.parallel.num_chunks)
    else:
        loader_class = LogLoader
        loader_kwargs = dict()

    loader = loader_class(file=file, multiple=multiple, **loader_kwargs)
    return loader.parse_log()
