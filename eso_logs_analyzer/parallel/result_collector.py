class ResultCollector(object):
    """
    Collects results of parallel tasks and aggregates them into some kind of final result.
    """

    def collect_result(self, result) -> None:
        """
        Processes the result in some way.
        @param result: Result data produced by a parallel task.
        """
        raise NotImplementedError

    def aggregated_result(self):
        """
        Aggregates the results produced by parallel tasks and returns the aggregation.
        @return: The aggregated result.
        """
        raise NotImplementedError

    def is_completed(self) -> bool:
        """
        Returns if all results were collected or not.
        @return: True, if all tasks were completed.
        """
        raise NotImplementedError
