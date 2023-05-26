from multiprocessing import Process
from multiprocessing.queues import Queue
from queue import Empty
from typing import Callable


class ParallelProcess(Process):
    __TQDM_INDEX_KWARG: str = "tqdm_index"

    def __init__(self,
                 input_queue: Queue,
                 output_queue: Queue,
                 task_function: Callable,
                 index: int,
                 set_tqdm_index: bool = False,
                 task_function_args: list = None,
                 task_function_kwargs: dict = None,
                 *args, **kwargs):
        """
        A process that performs a task in parallel.
        @param input_queue: Queue containing input objects. If empty no further objects need to be processed and the process can exit.
        @param output_queue: Queue to which result data is pushed.
        @param task_function: Function that is performed on each input object.
        @param index: Index of the process for parallel tqdm output.
        @param set_tqdm_index: If set to true the task function is passed the index of the process as parameter 'tqdm_index' to allow parallel tqdm progress bars.
        @param task_function_args: Positional arguments that are passed to the task function.
        @param task_function_kwargs: Keyword arguments that are passed to the task function.
        """

        super().__init__(*args, **kwargs)
        self.input_queue = input_queue
        self.output_queue = output_queue

        self.task_function = task_function
        # Create copies of these collections, since they are otherwise shared between processes and we may need to modify it for the tqdm index.
        self.task_function_args = list(task_function_args) if task_function_args else []
        self.task_function_kwargs = dict(task_function_kwargs) if task_function_kwargs else {}

        if set_tqdm_index:
            # Increment position by one, as the parallel task object that spawned this process will write to position 0
            self.task_function_kwargs[self.__TQDM_INDEX_KWARG] = index + 1

    def run(self):
        while True:
            try:
                input_object = self.input_queue.get()
                self.output_queue.put(self.task_function(input_object, *self.task_function_args, **self.task_function_kwargs))
            except Empty:
                break
