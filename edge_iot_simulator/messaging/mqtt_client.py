from enum import Enum
from json.decoder import JSONDecodeError
from multiprocessing.sharedctypes import Value
from ssl import TLSVersion
from typing import KeysView
import paho.mqtt.client as mqtt
import logging
import threading
import os
import json
import time
import copy
import ssl
import datetime
import jwt
from settings import *

logging.basicConfig(format='%(asctime)s %(module)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_gcp_jwt():
    """Creates a JWT (https://jwt.io) to establish an MQTT connection.
    Args:
     algorithm: The encryption algorithm to use. Either 'RS256' or 'ES256'
    Returns:
        A JWT generated from the given project_id and private key, which
        expires in 20 minutes. After 20 minutes, your client will be
        disconnected, and a new JWT will have to be generated.
    Raises:
        ValueError: If the private_key_file does not contain a known key.
    """
    if os.getenv('JWT_EXP_IN_MINUTES'):
        minutes = int(os.getenv('JWT_EXP_IN_MINUTES'))
    else:
        minutes = 20
    token = {
        # The time that the token was issued at
        "iat": datetime.datetime.now(tz=datetime.timezone.utc),
        # The time the token expires.
        "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=minutes),
        # The audience field should always be set to the GCP project id.
        "aud": os.getenv('GCP_PROJECT_ID'),
    }
    
    # Read the private key file.
    with open(os.getenv('MQTT_PASSWORD'), "r") as f:
        private_key = f.read()

    if os.getenv('JWT_ALG'):
        algo = os.getenv('JWT_ALG')
    else:
        algo = "RS256"
    jwt_key = jwt.encode(token, private_key, algorithm=algo)
    return jwt_key

class MqttClient(threading.Thread):

    def __init__(self, queue, consumer_queue):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        self.exit_event = threading.Event()
        self.queue = queue
        self.consumer_queue = consumer_queue
        self.client = self.init_mqtt()
        self.mqtt_message_counter = 0

    def init_mqtt(self):
        client = mqtt.Client(client_id=os.getenv('MQTT_CLIENT_ID'), clean_session=False)
        if (os.getenv('MQTT_USERNAME') is not None and os.getenv('MQTT_PASSWORD') is not None):
            if os.getenv('MQTT_PASSWORD').endswith('.pem'):
                password = create_gcp_jwt()
            else:
                password = os.getenv('MQTT_PASSWORD') 

            client.username_pw_set(username=os.getenv('MQTT_USERNAME'), password=password)

        if(os.getenv('MQTT_TLS') == 'True'):
            ca_certs = os.getenv('MQTT_CA_CERTS') if os.getenv('MQTT_CA_CERTS') is not None else None
            certfile = os.getenv('MQTT_CERTFILE') if os.getenv('MQTT_CERTFILE') is not None else None
            keyfile = os.getenv('MQTT_KEYFILE') if os.getenv('MQTT_KEYFILE') is not None else None
            cert_reqs = ssl.CERT_REQUIRED if os.getenv('MQTT_CERT_REQ') == 'True' else ssl.CERT_OPTIONAL

            client.tls_set(ca_certs=ca_certs, certfile=certfile, keyfile=keyfile, cert_reqs=cert_reqs, tls_version=ssl.PROTOCOL_TLSv1_2)

            if (os.getenv('MQTT_TLS_INSECURE') == 'True'):
                client.tls_insecure_set(True)
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_publish = self.on_publish
        client.on_message = self.on_message
        client.reconnect_delay_set(min_delay=1, max_delay=3600)

        return client

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Publisher connected with result code " + str(rc))
        
        self.logger.info("Subscribe to topics...")
        if os.getenv('CUSTOM_TOPIC_ALL_RES'):
            self.client.subscribe(os.getenv('CUSTOM_TOPIC_ALL_RES'), int(os.getenv('MQTT_SUBSCRIBE_QOS')))
        else:
            self.client.subscribe(topic_cpuLoadSvc_cpuLoadJob_create_req, int(os.getenv('MQTT_SUBSCRIBE_QOS')))
            self.client.subscribe(topic_cpuLoadSvc_cpuLoadJob_read_req, int(os.getenv('MQTT_SUBSCRIBE_QOS')))
            self.client.subscribe(topic_cpuLoadSvc_cpuLoadJob_delete_req, int(os.getenv('MQTT_SUBSCRIBE_QOS')))
            
    def on_disconnect(self, client, userdata, rc):
        if (rc != 0):
           self.logger.error('Unexpected disconnect: ' + str(rc))

    def on_publish(self, client, userdata, mid):
        with self.lock:
            self.mqtt_message_counter += 1
        self.logger.info("Successfully published message {}".format(str(mid)))

    def on_message(self, client, userdata, msg):
        self.logger.info('Received new message, topic: {}, message: {}'.format(msg.topic, msg.payload))
        self.consumer_queue.put(MqttMessage(msg.topic, msg.payload))

    def run(self):
        self.logger.debug("Successfully started mqtt publisher...")
        try:
            self.client.connect(os.getenv('MQTT_SERVER_NAME'), int(os.getenv('MQTT_PORT')))
            self.client.loop_start()
            
            # TODO: add further try-catch
            while not self.exit_event.is_set():
                mqtt_message = self.queue.get()
                if (mqtt_message.topic == topic_mqtt_client_publisher_state and mqtt_message.payload == "stopped"):
                    return
                else:
                    topic = mqtt_message.topic
                    payload = mqtt_message.payload
                    self.client.publish(topic, payload, int(os.getenv('MQTT_PUBLISH_QOS')))
        except Exception as e:
            self.logger.error('Error establishing connection to {}:{}, {}'.format(os.getenv('MQTT_SERVER_NAME'),os.getenv('MQTT_PORT'),str(e)))

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
        self.queue.put(MqttMessage(topic_mqtt_client_publisher_state, "stopped"))
        if (self.lock.locked()):
            self.lock.release()

class MessageBroker(threading.Thread):

    def __init__(self, consumer_queue, publisher_queue, cpu_load_svc):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.consumer_queue = consumer_queue
        self.lock = threading.Lock()
        self.exit_event = threading.Event()
        self.cpu_load_svc = cpu_load_svc
        self.publisher_queue = publisher_queue

    def run(self):
        while not self.exit_event.is_set():
            item = self.consumer_queue.get()

            mqtt_message = None
            if (isinstance(item, MqttMessage)):
                mqtt_message = item
            elif (item == 'shutdown'):
                return
            else:
                self.logger.error('Unknown message received!')

            try:
                if (mqtt_message.topic == topic_cpuLoadSvc_cpuLoadJob_create_req):
                        response_topic = topic_cpuLoadSvc_cpuLoadJob_create_res
                        json_cpu_load_job_all_cores=json.loads(mqtt_message.payload.decode())
                        if (json_cpu_load_job_all_cores['duration'] is None):
                            raise ValueError('duration is missing')
                        elif (json_cpu_load_job_all_cores['target_load'] is None):
                            raise ValueError('target_load is missing')
                        else:
                            created_cpu_load_job = self.cpu_load_svc.create_cpu_load_job(json_cpu_load_job_all_cores['duration'], json_cpu_load_job_all_cores['target_load'])
                            self.publisher_queue.put(MqttMessage(topic_cpuLoadSvc_cpuLoadJob_create_res, MqttSuccessMessage(created_cpu_load_job).to_json()))

                elif (mqtt_message.topic == topic_cpuLoadSvc_cpuLoadJob_read_req):
                    response_topic = topic_cpuLoadSvc_cpuLoadJob_read_res
                    self.publisher_queue.put(MqttMessage(topic_cpuLoadSvc_cpuLoadJob_read_res, MqttSuccessMessage(self.cpu_load_svc.get_cpu_load_job_history()).to_json()))

                elif (mqtt_message.topic == topic_cpuLoadSvc_cpuLoadJob_delete_req):
                    response_topic = topic_cpuLoadSvc_cpuLoadJob_delete_res
                    if (len(mqtt_message.payload) == 0):
                        raise ValueError('payload is missing')

                    json_cpu_load_job_delete_req = json.loads(mqtt_message.payload.decode())
                    if (json_cpu_load_job_delete_req['id'] is None ):
                        raise ValueError('id is missing')
                    self.publisher_queue.put(MqttMessage(topic_cpuLoadSvc_cpuLoadJob_delete_res, MqttSuccessMessage(self.cpu_load_svc.delete_cpu_load_job_by_id(json_cpu_load_job_delete_req['id'])).to_json()))

            except (ValueError, JSONDecodeError, KeyError) as e:
                error_message = 'Illegal message received: ' + str(e)
                self.logger.error(error_message)
                self.publisher_queue.put(MqttMessage(response_topic, MqttErrorMessage(error_message).to_json()))
                

    def stop(self):
        self.logger.info('Message broker received shutdown signal...')

        while not self.consumer_queue.empty():
            self.consumer_queue.get()
        self.consumer_queue.put('shutdown')

        self.exit_event.set()

class MqttMessage():

    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

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
        return json.dumps(self, default=lambda o: o.__dict__)

    def to_string(self):
        return str(self.to_json())

class MqttSuccessMessage():

    def __init__(self, success):
        self.success = success

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def to_string(self):
        return str(self.to_json())

class MqttErrorMessage():

    def __init__(self, error):
        self.error = error

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def to_string(self):
        return str(self.to_json())

class MqttException(Exception):
    pass
