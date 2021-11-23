from enum import Enum
import json
import logging
import copy
import multiprocessing
from multiprocessing import process
import os
import signal
import threading
import time
import psutil
import queue
from cpu_load_generator import load_single_core, load_all_cores, from_profile
from messaging.mqtt_publisher import MqttMessage

logging.basicConfig(format='%(asctime)s %(module)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

class CPULoadService(threading.Thread):

    def __init__(self, consumer_queue):
        threading.Thread.__init__(self)
        self.consumer_queue = consumer_queue
        self.lock = threading.RLock()
        self.exit_event = threading.Event()
        self.logger = logging.getLogger(__name__)
        self.proc = None
        self.CPULoadJobQueue = queue.Queue()
        self.CPULoadJobHistory = {}
        self.job_count = 0
        self.CPULoadJobRunner = None
        self.current_job_id = None

    def run(self):
        self.logger.debug("Successfully started CPULoadService...")
        self.CPULoadJobRunner = threading.Thread(target=self.run_cpu_load_job, args=())
        self.CPULoadJobRunner.start()
        while not self.exit_event.is_set():
            item = self.consumer_queue.get()

            new_cpu_load_job_all_cores = None
            if (isinstance(item, CPULoadJobAllCores)):
                new_cpu_load_job_all_cores = item
            elif (item == 'shutdown'):
                return
            else:
                self.logger.error('Unknown message received!')

            self.logger.info('Received new CPULoadJobAllCores: {}'.format(new_cpu_load_job_all_cores.to_string()))
            with self.lock:
                self.job_count += 1
                created_cpu_load_job_all_cores = QueuedCPULoadJobAllCores(new_cpu_load_job_all_cores.duration, new_cpu_load_job_all_cores.target_load, self.job_count, None, CPULoadJobStates.CREATED.name)
                self.CPULoadJobHistory[created_cpu_load_job_all_cores.id] = created_cpu_load_job_all_cores
            self.CPULoadJobQueue.put(created_cpu_load_job_all_cores)

    def run_cpu_load_job(self):
        self.logger.debug('Successfully started CPULoadJobRunner...')
        while not self.exit_event.is_set():
            self.logger.debug('CPULoadJobRunner is waiting for incoming jobs...')
            item = self.CPULoadJobQueue.get()

            if (isinstance(item, QueuedCPULoadJobAllCores)):
                new_queued_cpu_load_job_all_cores = item
                self.logger.info('Received new QueuedCPULoadJobAllCores: {}'.format(new_queued_cpu_load_job_all_cores.to_string()))            
            elif (item == 'shutdown'):
                return
            else:
                self.logger.error('Unknown message received!')

            with self.lock:
                if self.CPULoadJobHistory[new_queued_cpu_load_job_all_cores.id].state == CPULoadJobStates.ABORTED.name:
                    self.logger.debug('Received already aborted job: {}'.format(self.CPULoadJobHistory[new_queued_cpu_load_job_all_cores.id]))
                    continue 

            self.proc = multiprocessing.Process(target=load_all_cores, args=(new_queued_cpu_load_job_all_cores.duration, new_queued_cpu_load_job_all_cores.target_load))
            self.proc.start()
            current_pid = self.proc.pid
            with self.lock:
                queued_cpu_load_job_all_cores = QueuedCPULoadJobAllCores(new_queued_cpu_load_job_all_cores.duration, new_queued_cpu_load_job_all_cores.target_load, new_queued_cpu_load_job_all_cores.id, current_pid, CPULoadJobStates.RUNNING.name)
                self.CPULoadJobHistory[queued_cpu_load_job_all_cores.id] = queued_cpu_load_job_all_cores
                self.current_job_id = queued_cpu_load_job_all_cores.id
            self.logger.info('Started new QueuedCPULoadJobAllCores {}'.format(queued_cpu_load_job_all_cores.to_string()))
            self.proc.join()
            with self.lock:
                if (self.CPULoadJobHistory[self.current_job_id].state != CPULoadJobStates.ABORTED.name):
                    self.CPULoadJobHistory[self.current_job_id].state = CPULoadJobStates.TERMINATED.name
                    self.logger.info('{} QueuedCPULoadJobAllCores {}'.format(self.CPULoadJobHistory[self.current_job_id].state, queued_cpu_load_job_all_cores.to_string()))

    def stop_current_CPULoadJob(self):
        if self.proc is not None and self.proc.pid > 0 and self.proc.is_alive():
            self.logger.info('Stop current CPULoadJob with parent pid {}'.format(self.proc.pid))
            with self.lock:
                self.CPULoadJobHistory[self.current_job_id].state = CPULoadJobStates.ABORTED.name
            parent = psutil.Process(self.proc.pid)
            current_process = os.getpid()
            children = parent.children(recursive=True)
            for p in children:
                if (p.pid != current_process):
                    p.terminate()
            self.proc.terminate()
            self.proc.join()
            self.logger.info('Successfully stopped CPULoadJob with parent pid {}'.format(self.proc.pid))
            self.proc = None

    def stop(self):
        self.logger.info('CPU load service received shutdown signal...')

        while not self.consumer_queue.empty():
            self.consumer_queue.get()
        self.consumer_queue.put('shutdown')

        while not self.CPULoadJobQueue.empty():
            self.CPULoadJobQueue.get()
        self.CPULoadJobQueue.put('shutdown')

        self.exit_event.set()

        if self.proc is not None and self.proc.pid > 0 and self.proc.is_alive():
            self.stop_current_CPULoadJob()
        
        self.CPULoadJobRunner.join()

    def create_cpu_load_job(self, duration, target_load):
        new_cpu_load_job_all_cores = CPULoadJobAllCores(duration, target_load)
        self.consumer_queue.put(new_cpu_load_job_all_cores)

    def get_cpu_load_job_history(self):
        with self.lock:
            return copy.deepcopy(self.CPULoadJobHistory)

    def delete_cpu_load_job_by_id(self, id):
        id = int(id)
        with self.lock:
            if id in self.CPULoadJobHistory and self.proc is not None and self.proc.is_alive():
                if self.CPULoadJobHistory[id].state == CPULoadJobStates.RUNNING.name:
                    self.stop_current_CPULoadJob()
                self.CPULoadJobHistory[id].state = CPULoadJobStates.ABORTED.name
                

class CPULoadJobAllCores():

    def __init__(self, duration, target_load):
        self.duration = duration
        self.target_load = target_load

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_string(self):
        return str(self.to_json())

class QueuedCPULoadJobAllCores(CPULoadJobAllCores):

    def __init__(self, duration, target_load, id, pid, state):
        super().__init__(duration, target_load)
        self.id = id
        self.pid = pid
        self.state = state

class CPULoadJobStates(Enum):
    CREATED = 1
    RUNNING = 2
    ABORTED = 3
    TERMINATED = 4

class CPULoadServiceServiceException(Exception):
    pass
