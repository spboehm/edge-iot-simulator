from datetime import datetime
from enum import Enum
import threading
import time
import random
import json
import copy
import logging
import os
import sys

from messaging.mqtt_client import MqttMessage
logging.basicConfig(format='%(asctime)s %(module)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

class TemperatureService(threading.Thread):
    
    def __init__(self, queue, interval, unit):
        threading.Thread.__init__(self)
        self.queue = queue
        self.interval = interval
        self.unit = unit
        self.last_temperature_measurement = None
        self.lock = threading.Lock()
        self.exit_event = threading.Event()
        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.debug("Successfully started temperature sensor...")
        while not self.exit_event.is_set():
            # temperature will be generated in celsius by default
            temperature_celsius = random.randrange(0,60)
            actual_temperature_measurement = None

            if (self.unit == TemperatureUnits.celsius.name):
                # put in queue
                actual_temperature_measurement = TemperatureMeasurement(time.time(),temperature_celsius,TemperatureUnits.celsius.name)
                self.create_mqtt_message(actual_temperature_measurement)
            else:
                actual_temperature_measurement = TemperatureMeasurement(time.time(),temperature_celsius,TemperatureUnits.fahrenheit.name)
                self.create_mqtt_message(actual_temperature_measurement.convert(TemperatureUnits.fahrenheit.name))
            
            with self.lock:
                self.last_temperature_measurement = actual_temperature_measurement
                self.logger.info("New value measured " + self.last_temperature_measurement.to_string())

            time.sleep(self.interval)
        
    def stop(self):
        self.exit_event.set()
        self.logger.info('Temperature service received shutdown signal...')


    def get_temperature(self, unit):
        with self.lock:
            if (self.last_temperature_measurement is not None):
                temperature_measurement = copy.deepcopy(self.last_temperature_measurement)

        if (self.last_temperature_measurement is None):
            temperature_measurement = TemperatureMeasurement(time.time(), float('inf'), TemperatureUnits.celsius.name)

        return temperature_measurement.convert(unit)

    def create_mqtt_message(self, temperature_measurement):
        self.queue.put(MqttMessage(os.getenv('MQTT_TOPIC_SENSORS')+'/'+os.getenv('MQTT_CLIENT_ID')+'/'+os.getenv('MQTT_TOPIC_SENSORS_DATA'), temperature_measurement.to_json()))

class TemperatureMeasurement():

    def __init__(self, timestamp, value, unit):
        self.timestamp = timestamp
        self.value = value
        self.unit = unit

    def convert(self, unit):
        if(unit == self.unit):
            return self

        if (unit == TemperatureUnits.celsius.name):
            return self.fahrenheit_to_celsius(self.value)
        else:
            return self.celsius_to_fahrenheit(self.value)

    def celsius_to_fahrenheit(self, temperature):
        self.value = (temperature * 1.8) + 32
        self.unit = TemperatureUnits.fahrenheit.name
        return self
    
    def fahrenheit_to_celsius(self, temperature):
        self.value = (temperature - 32) * (5 / 9)
        self.unit = TemperatureUnits.celsius.name
        return self

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def to_string(self):
        return str(self.to_json())

class TemperatureUnits(Enum):
    celsius = 1
    fahrenheit = 2

class TemperatureServiceException(Exception):
    pass
