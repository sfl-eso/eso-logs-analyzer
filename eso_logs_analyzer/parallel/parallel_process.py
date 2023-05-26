from multiprocessing import Process
from multiprocessing.queues import Queue
from queue import Empty
from typing import Callable


class ParallelProcess(Process):
    def __init__(self,
                 input_queue: Queue,
                 output_queue: Queue,
                 task_function: Callable,
                 task_function_args: list = None,
                 task_function_kwargs: dict = None,
                 *args, **kwargs):
        """
        A process that performs a task in parallel.
        @param input_queue: Queue containing input objects. If empty no further objects need to be processed and the process can exit.
        @param output_queue: Queue to which result data is pushed.
        @param task_function: Function that is performed on each input object.
        @param task_function_args: Positional arguments that are passed to the task function.
        @param task_function_kwargs: Keyword arguments that are passed to the task function.
        """
        super().__init__(*args, **kwargs)
        self.input_queue = input_queue
        self.output_queue = output_queue

        self.task_function = task_function
        self.task_function_args = task_function_args or []
        self.task_function_kwargs = task_function_kwargs or {}

    def run(self):
        while True:
            try:
                input_object = self.input_queue.get()
                self.output_queue.put(self.task_function(input_object, *self.task_function_args, **self.task_function_kwargs))
            except Empty:
                break
