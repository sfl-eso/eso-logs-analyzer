from __future__ import annotations

from multiprocessing import Queue
from typing import Callable, TYPE_CHECKING

from tqdm import tqdm

from .empty_collector import EmptyCollector
from .parallel_process import ParallelProcess

if TYPE_CHECKING:
    from .result_collector import ResultCollector


class ParallelTask:
    def __init__(self,
                 description: str,
                 num_processes: int,
                 input_objects: list,
                 task_function: Callable,
                 result_collector: ResultCollector = None,
                 task_function_args: list = None,
                 task_function_kwargs: dict = None,
                 set_tqdm_index: bool = False):
        """
        Performs a task in parallel using the multiprocessing framework.
        @param num_processes: Number of processes to use.
        @param input_objects: List of input objects that are passed as input to the processed performing the task.
        @param task_function: Function that is executed in a process. Takes an input object as input and produces some kind of output.
        @param result_collector: Processes result output produced by each process and aggregates the results into some kind of final result.
               If unset, an empty collector is used that does not return any results.
        @param set_tqdm_index: If set to True, the keyword argument 'tqdm_index' is passed to the task function with the
               position for a tqdm progress bar.
        """
        super().__init__()
        self.description = description
        self.input_objects = input_objects
        self.result_collector: ResultCollector = result_collector or EmptyCollector(len(input_objects))

        self.input_queue = Queue()
        self.output_queue = Queue()

        task_function_args = task_function_args or []
        task_function_kwargs = task_function_kwargs or {}

        # Don't create more processes than necessary if there are not enough tasks.
        num_processes = min(num_processes, len(input_objects))
        self.processes = []
        for index in range(num_processes):
            self.processes.append(ParallelProcess(index=index,
                                                  set_tqdm_index=set_tqdm_index,
                                                  input_queue=self.input_queue,
                                                  output_queue=self.output_queue,
                                                  task_function=task_function,
                                                  task_function_args=task_function_args,
                                                  task_function_kwargs=task_function_kwargs))

    def execute(self):
        progress_bar = tqdm(total=len(self.input_objects), desc=self.description)

        # Populate input queue
        for datum in self.input_objects:
            self.input_queue.put(datum)

        # Start processes
        for process in self.processes:
            process.start()

        # Wait for all processes to finish
        while not self.result_collector.is_completed():
            result = self.output_queue.get(block=True)
            self.result_collector.collect_result(result)
            progress_bar.update(1)

        # Kill all processes
        for process in self.processes:
            process.kill()

        return self.result_collector.aggregated_result()
