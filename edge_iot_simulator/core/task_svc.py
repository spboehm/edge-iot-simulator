from enum import Enum
import json
import logging
import copy
import multiprocessing
from multiprocessing import process
from multiprocessing.sharedctypes import Value
import os
import signal
import threading
import time
from typing import ValuesView
import requests
import queue
import random

logging.basicConfig(format='%(asctime)s %(module)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

class TaskService(threading.Thread):

    def __init__(self, publisher_queue, cpu_load_svc):
        threading.Thread.__init__(self)
        self.input_queue = queue.Queue()
        self.publisher_queue = publisher_queue
        self.lock = threading.RLock()
        self.exit_event = threading.Event()
        self.logger = logging.getLogger(__name__)
        self.proc = None
        self.taskQueue = queue.Queue()
        self.taskHistory = {}
        self.taskCount = 0
        self.currentTaskId = None
        self.cpu_load_svc = cpu_load_svc

    def run(self):
        self.logger.debug("Successfully started TaskService")
        while not self.exit_event.is_set():
            item = self.input_queue.get()

            new_task = None
            if (isinstance(item, Task)):
                new_task = item
            elif (item == "shutdown"):
                return
            else:
                self.logger.error('Unknown message received!')

            self.logger.info('Received new Task: {}'.format(new_task.to_string()))
            with self.lock:
                # TODO: Resolve oversimplification
                currentTaskId = self.taskCount
                self.taskCount += 1
                wait_time = random.uniform(0.5, 3.5)
                self.logger.debug(f"Waiting for {wait_time} seconds to simulate processing the task.")
                time.sleep(wait_time)
                # TODO: refactor request

    def stop(self):
        while not self.input_queue.empty():
            self.input_queue.get()
        self.input_queue.put('shutdown')
        
        self.exit_event.set()
        self.logger.info('Task service received shutdown signal...')

    def create_task(self, uuid):
        self.logger.debug('TaskService received new task with uuid {}'.format(uuid))
        new_task = Task(uuid)
        self.input_queue.put(new_task)
        return new_task

class Task():
    def __init__(self, uuid):
        self.uuid = uuid

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_string(self):
        return str(self.to_json())
    


