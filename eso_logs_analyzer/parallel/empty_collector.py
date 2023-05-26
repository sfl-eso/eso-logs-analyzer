from .result_collector import ResultCollector


class EmptyCollector(ResultCollector):
    """
    Emtpy collector that just provides functionality to check if all tasks are finished.
    """

    def __init__(self, num_tasks: int):
        super().__init__()
        self.num_tasks = num_tasks

    def collect_result(self, result):
        self.num_tasks -= 1

    def aggregated_result(self):
        return None

    def is_completed(self) -> bool:
        return self.num_tasks == 0
