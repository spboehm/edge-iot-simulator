from enum import Enum
import paho.mqtt.client as mqtt
import logging
import threading
import os
import json
import time
import copy

logging.basicConfig(format='%(asctime)s %(module)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MqttPublisher(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        self.exit_event = threading.Event()
        self.queue = queue
        self.client = self.init_mqtt()
        self.mqtt_message_counter = 0

    def init_mqtt(self):
        client = mqtt.Client(client_id=os.getenv('MQTT_CLIENT_ID'), clean_session=False)
        if (os.getenv('MQTT_USERNAME') is not None and os.getenv('MQTT_PASSWORD') is not None):
            client.username_pw_set(username=os.getenv('mosquitto_username'), password=os.getenv('mosquitto_password'))
        if(os.getenv('MQTT_TLS') == 'True'):
            client.tls_set()
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.reconnect_delay_set(min_delay=1, max_delay=3600)

        return client

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Publisher connected with result code " + str(rc))

    def on_disconnect(self, client, userdata, rc):
        if (rc != 0):
           self.logger.error('Unexpected disconnect: ' + str(rc))

    def run(self):
        self.logger.debug("Successfully started mqtt publisher...")
        try:
            self.client.connect(os.getenv('MQTT_SERVER_NAME'), int(os.getenv('MQTT_PORT')))
            self.client.loop_start()
            while not self.exit_event.is_set():
                mqtt_message = self.queue.get()
                if (os.getenv('MQTT_TOPIC_PUBLISHER')+'/'+os.getenv('MQTT_CLIENT_ID')+'/'+os.getenv('MQTT_TOPIC_PUBLISHER_STATE')):
                    if (mqtt_message.payload == "stopped"):
                        return
                    else:
                        topic = mqtt_message.topic
                        payload = mqtt_message.payload
                        mqtt_message_info = self.client.publish(topic, json.dumps(payload.to_json()), int(os.getenv('MQTT_PUBLISH_QOS')))
                        mqtt_message_info.wait_for_publish()
                        if (mqtt_message_info.is_published()):
                            with self.lock:
                                self.mqtt_message_counter += 1
                                logger.info("Successfully published message {}".format(payload.to_string()))
        except Exception as e:
            self.logger.error('Error establishing connection to {}:{}'.format(os.getenv('MQTT_SERVER_NAME'),os.getenv('MQTT_PORT')) + str(e))

    def get_status(self):
        if (self.client.is_connected()):
            return MqttStatus.connected.name
        else:
            return MqttStatus.disconnected.name

    def get_mqtt_message_counter(self):
        with self.lock:
            return self.mqtt_message_counter

    def get_mqtt_statistics(self):
        return copy.deepcopy(MqttStatistics(self.get_status(), self.get_mqtt_message_counter()))

    def stop(self):
        self.logger.info("mqtt publisher received shutdown signal")
        self.exit_event.set()
        self.client.loop_stop()
        self.client.disconnect()
        self.queue.put(MqttMessage(os.getenv("MQTT_TOPIC_PUBLISHER")+'/'+os.getenv('MQTT_CLIENT_ID') + '/' +os.getenv('MQTT_TOPIC_PUBLISHER_STATE'), "stopped"))
        if (self.lock.locked()):
            self.lock.release()

class MqttMessage():

    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_string(self):
        return str(self.to_json())

class MqttStatus(Enum):
    connected = 1
    disconnected = 2

class MqttStatistics():
    def __init__(self, status, message_counter):
        self.host = os.getenv('MQTT_SERVER_NAME')
        self.port = os.getenv('MQTT_PORT')
        self.tls = os.getenv('MQTT_TLS')
        self.status = status
        self.message_counter = message_counter

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_string(self):
        return str(self.to_json())

class MqttException(Exception):
    pass
