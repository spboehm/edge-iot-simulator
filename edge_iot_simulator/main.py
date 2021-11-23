#!/usr/bin/env python3
from core.temperature_svc import TemperatureMeasurement, TemperatureService,TemperatureUnits
from core.cpu_load_svc import CPULoadJobAllCores, CPULoadService
from messaging.mqtt_publisher import MqttException, MqttPublisher, MqttStatus
from web.app import WebApp

import logging
import os
import random
import queue
import time
from dotenv import load_dotenv
import signal
import time
import sys

logging.basicConfig(format='%(asctime)s %(module)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
load_dotenv()

if __name__=="__main__":

    publisher_queue = queue.Queue()
    consumer_queue = queue.Queue()

    publisher = MqttPublisher(publisher_queue)
    temperature_svc = TemperatureService(publisher_queue, 3, TemperatureUnits.celsius.name)
    cpuload_svc = CPULoadService(consumer_queue)
    web_app = WebApp(publisher, temperature_svc)
    
    try:
        logging.info('Please press any key to interrupt...')
        publisher.start()
        temperature_svc.start()
        cpuload_svc.start()
        web_app.start()
        time.sleep(5) # wait for connection to mqtt broker
        if(publisher.get_mqtt_statistics().status == MqttStatus.disconnected.name):
            raise Exception("Could not establish the connection to the mqtt broker...") 

        time.sleep(5)
        consumer_queue.put(CPULoadJobAllCores(15, 0.65))
        time.sleep(5)
        cpuload_svc.stop_current_CPULoadJob()
        consumer_queue.put(CPULoadJobAllCores(20, 0.80))

        signal.pause()
    except KeyboardInterrupt as e:
        logging.info("Received user's shutdown signal...")
    except Exception as e:
        logging.error("Unknown error occurred: " + str(e))
    finally:
        publisher.stop()
        temperature_svc.stop()
        cpuload_svc.stop()
        web_app.stop()

        logging.info('Wait for graceful termination...')
        
        publisher.join()
        temperature_svc.join()
        cpuload_svc.join()
        web_app.join()

    logging.info('Successfully terminated edge-iot simulator')
