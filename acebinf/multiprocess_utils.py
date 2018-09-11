"""
Convience objects to start a multi processed consumer/producer strategy
"""
import sys
import traceback
import multiprocessing
import logging


class Consumer(multiprocessing.Process):

    """
    Basic Consumer. Follow the two queues with your *args and **kwargs that should be sent
    to the task when __call__ 'd

    NOTE! args can't hold anything that isn't pickle-able for the subprocess
    task_queue, result_queue

    Should add timeout functionality - I know I have it somewhere
    """

    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        try:
            while True:
                next_task = self.task_queue.get()
                if next_task is None:
                    # Poison pill means shutdown
                    self.task_queue.task_done()
                    break
                try:
                    next_task()
                except Exception as e:  # pylint: disable=broad-except
                    logging.error("Exception raised in task - %s", str(e))

                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    logging.error("Dumping Traceback:")
                    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

                    next_task.failed = True
                    next_task.errMessage = str(e)

                self.result_queue.put(next_task)
                self.task_queue.task_done()

            return
        except Exception as e:  # pylint: disable=broad-except
            logging.error("Consumer %s Died\nERROR: %s", self.name, e)
            return


class ConsumerPool(object):

    """
    A resource for making a pool of consumer multiprocesses

    The tasks passed in via put must be callable (__call__)
    finished tasks are then yielded back.

    Usage:
    >>> procs = ConsumerPool(THREADS)
    >>> procs.start_pool()
    >>> for stuff in things:
    >>>     procs.put_task(MyTask(stuff, Param1, Param2))
    >>> procs.put_poison()
    >>>
    >>> for pcmp_result in procs.get_tasks():
    >>>     pass # Do work on your MyTasks
    """

    def __init__(self, threads=1):
        """
        Does all the work
        """
        self.threads = threads
        self.input_queue = multiprocessing.JoinableQueue()
        self.output_queue = multiprocessing.Queue()
        self.processes = [Consumer(self.input_queue, self.output_queue)
                          for i in range(self.threads)]  # pylint: disable=unused-variable
        self.task_count = 0

    def start_pool(self):
        """
        run start on all processes
        """
        for proc in self.processes:
            proc.start()

    def put_task(self, task):
        """
        Add a callable task to the input_queue
        """
        self.task_count += 1
        self.input_queue.put(task)

    def put_poison(self):
        """
        For each process, add a poison pill so that it will close
        once the input_queue is depleted
        """
        for i in range(self.threads):
            logging.debug("Putting poison %d", i)
            self.input_queue.put(None)

    def get_tasks(self):
        """
        Yields the finished tasks
        """
        remaining = self.task_count
        while remaining:
            ret_task = self.output_queue.get()
            remaining -= 1
            yield ret_task
