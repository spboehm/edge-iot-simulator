import threading
import logging
import queue
import requests
import time
import uuid
import os
import json
from messaging.mqtt_client import MqttMessage
import multiprocessing
from multiprocessing import process
from multiprocessing.sharedctypes import Value

logging.basicConfig(format='%(asctime)s %(module)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

def getTimeStamp():
    posix_timestamp = int(time.time_ns())
    return(posix_timestamp)

class RequestService(threading.Thread):

    def __init__(self, publisher_queue):
        threading.Thread.__init__(self)
        self.input_queue = queue.Queue()
        self.publisher_queue = publisher_queue
        self.lock = threading.RLock()
        self.exit_event = threading.Event()
        self.logger = logging.getLogger(__name__)
        self.proc = None
        self.requestJobQueue = queue.Queue()
        self.requestJobHistory = {}
        self.job_count = 0
        self.requestJobRunner = None
        self.current_job_id = None


    def run(self):
        self.logger.debug("Successfully started RequestService...")
        self.requestJobRunner = threading.Thread(target=self.run_request_job, args=())
        self.requestJobRunner.start()
        while not self.exit_event.is_set():
            item = self.input_queue.get()

            new_request_job = None
            if (isinstance(item, RequestJob)):
                new_request_job = item
            elif (item == 'shutdown'):
                return
            else:
                self.logger.error('Unknown message received!')

            self.logger.info('Received new RequestJob: {}'.format(new_request_job.to_string()))
            with self.lock:
                self.job_count += 1
                # TODO: QueuesJob
                # TODO: history
                self.requestJobQueue.put(new_request_job)

    def run_request_job(self):
        self.logger.debug('Successfully started RequestJobRunner...')
        while not self.exit_event.is_set():
            self.logger.debug('RequestRunner is waiting for incoming jobs...')
            item = self.requestJobQueue.get()

            if (isinstance(item, RequestJob)):
                new_queued_request_job = item
                self.logger.info('Received new RequestJob: {}'.format(new_queued_request_job.to_string()))      
            elif (item == 'shutdown'):
                return
            else:
                self.logger.error('Unknown message received!')
        
            while not self.exit_event.is_set():
                # send request
                self.logger.info('Started new RequestJob {}'.format(new_queued_request_job.to_string()))
                duration = self.request(new_queued_request_job.destinationHost, new_queued_request_job.resource, new_queued_request_job.count)
                requestMetric = RequestMetric(new_queued_request_job.destinationHost, new_queued_request_job.resource, duration, "ms")
                self.create_mqtt_message(requestMetric)
                time.sleep(new_queued_request_job.recurrence)
        
    def request(self, destinationHost, resource, count):
        startTime = getTimeStamp()
        for i in range(count):
            r = requests.get(destinationHost + resource, verify=False)
        endTime =  getTimeStamp()
        duration = ((endTime - startTime) / 1000000 / count)
        return duration
    
    def create_request_job(self, destinationHost, resource, count, recurrence):
        new_request_job = RequestJob(destinationHost, resource, count, recurrence)
        self.input_queue.put(new_request_job)
        return new_request_job
    
    def create_mqtt_message(self, requestMetric):
        self.publisher_queue.put(MqttMessage("dt/pulceo/requests", requestMetric.to_json()))

    def stop(self):
        self.logger.info('CPU load service received shutdown signal...')
        while not self.input_queue.empty():
            self.input_queue.get()
        self.input_queue.put('shutdown')
        while not self.requestJobQueue.empty():
            self.requestJobQueue.get()
        self.requestJobQueue.put('shutdown')
        self.exit_event.set()
        self.requestJobRunner.join()

class RequestJob():
    def __init__(self, destinationHost, resource, count, recurrence):
        self.destinationHost = destinationHost
        self.resource = resource
        self.count = count
        self.recurrence = recurrence

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_string(self):
        return str(self.to_json())

class RequestMetric():
    def __init__(self, dest, resource, value, unit):
        self.requestUUID = str(uuid.uuid4())
        self.timestamp = getTimeStamp()
        self.requestType = "req_rtt"
        self.sourceHost = os.getenv('MQTT_CLIENT_ID')
        self.destinationHost = dest
        self.resource = resource
        self.value = value
        self.unit = unit

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_string(self):
        return str(self.to_json())

class RequestServiceException(Exception):
    pass