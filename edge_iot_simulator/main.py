#!/usr/bin/env python3
import argparse
from core.temperature_svc import TemperatureMeasurement, TemperatureService,TemperatureUnits
from core.cpu_load_svc import CPULoadJobAllCores, CPULoadService
from messaging.mqtt_client import MqttException, MqttClient, MqttStatus, MessageBroker
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


    parser = argparse.ArgumentParser(description='Edge-IoT Simulator')
    parser.add_argument('--service', metavar='S', choices=('temperature_svc', 'cpu_load_svc', 'all'), default='all', type=str, nargs='?', help='State the service you would like to start...')
    args = parser.parse_args()

    publisher_queue = queue.Queue()
    consumer_queue = queue.Queue()

    publisher = MqttClient(publisher_queue, consumer_queue)
    temperature_svc = TemperatureService(publisher_queue, 3, TemperatureUnits.celsius.name)
    cpu_load_svc = CPULoadService(publisher_queue)
    web_app = WebApp(publisher, temperature_svc, cpu_load_svc)
    message_broker = MessageBroker(consumer_queue, publisher_queue, cpu_load_svc)

    try:
        logging.info('Start Edge-IoT Simulator...')
        publisher.start()
        if vars(args)['service'] == "temperature_svc" or vars(args)['service'] == "all":
            temperature_svc.start()
        if vars(args)['service'] == "cpu_load_svc" or vars(args)['service'] == "all":
            cpu_load_svc.start()
        web_app.start()
        message_broker.start()
        time.sleep(5) # wait for connection to mqtt broker
        if(publisher.get_mqtt_statistics().status == MqttStatus.disconnected.name):
            raise Exception("Could not establish the connection to the mqtt broker...") 
        signal.pause()
    except KeyboardInterrupt as e:
        logging.info("Received user's shutdown signal...")
    except Exception as e:
        logging.error("Unknown error occurred: " + str(e))
    finally:
        publisher.stop()
        if vars(args)['service'] == "temperature_svc" or vars(args)['service'] == "all":
            temperature_svc.stop()
        if vars(args)['service'] == "cpu_load_svc" or vars(args)['service'] == "all":
            cpu_load_svc.stop()
        web_app.stop()
        message_broker.stop()

        logging.info('Wait for graceful termination...')
        
        publisher.join()
        if vars(args)['service'] == "temperature_svc" or vars(args)['service'] == "all":
            temperature_svc.join()
        if vars(args)['service'] == "cpu_load_svc" or vars(args)['service'] == "all":
            cpu_load_svc.join()
        web_app.join()
        message_broker.join()

    logging.info('Successfully terminated edge-iot simulator')
