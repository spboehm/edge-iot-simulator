#!/usr/bin/python3
import os
import csv
from paho.mqtt import client as mqtt_client
from core.request_svc import RequestJob
from settings import *
import random
import time
import ssl
import requests

broker = os.getenv('MQTT_SERVER_NAME')
port = int(os.getenv('MQTT_PORT'))
topic = "python/mqtt"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
    # For paho-mqtt 2.0.0, you need to add the properties parameter.
    # def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_OPTIONAL, tls_version=ssl.PROTOCOL_TLSv1_2)


    # For paho-mqtt 2.0.0, you need to set callback_api_version.
    # client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

if __name__ == '__main__':
    # open csv
    request_jobs= []
    with open(os.getcwd() + '/hosts.csv') as csv_file:
        request_jobs_as_csv = csv.DictReader(csv_file, delimiter=',')
        for request_job in request_jobs_as_csv:
            request_jobs.append(request_job)

    # check availability of eis
    for request_job in request_jobs:
        r = requests.get(request_job['destinationHost'] + request_job['resource'], verify=False)
        if r.status_code == 200:
            print('Host ' + request_job['destinationHost'] + ' available with code ' + str(r.status_code))
        else:
            print('Host ' + request_job['destinationHost'] + ' NOT available with code ' + str(r.status_code))
            exit(1)
    
    client = connect_mqtt()
    client.loop_start()

    time.sleep(10)

    # publish requests
    seq = 0
    for request_job in request_jobs:
        mqtt_client_id = request_job['topic']
        topic = f'services/requestSvc/{mqtt_client_id}/jobs/create/req'
        request_job = RequestJob(request_job['destinationHost'], request_job['resource'], request_job['count'], request_job['recurrence'])
        client.publish(topic, request_job.to_json())
        print('Sent RequestJob ' + request_job.to_json() + ' to ' + topic)
        time.sleep(seq * 15)
        seq += 1

    client.loop_stop()