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
import json
import urllib.request, json
import argparse

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

    # args
    parser = argparse.ArgumentParser(prog='Edge-IoT-Simulator MQTT Manager')
    parser.add_argument('-f', '--filename', required=True)

    # parse args
    args = parser.parse_args()
    path = os.getcwd() + '/' + args.filename
    if not os.path.isfile(path):
        print('File ' + path + ' is not a file!')
        exit(1)
    
    # open csv
    request_jobs= []
    with open(path) as csv_file:
        request_jobs_as_csv = csv.DictReader(csv_file, delimiter=',')
        for request_job in request_jobs_as_csv:
            request_jobs.append(request_job)
    
    # applications.json
    nodeName_host_dict = {}
    with urllib.request.urlopen("http://localhost:8081/api/v1/applications") as url:
        applications_json = json.load(url)
        for application in applications_json:
            nodeName_host_dict[application['name']] = application['endpoint']
    
    # check availability of eis
    for request_job in request_jobs:
        r = requests.get(nodeName_host_dict[request_job['destinationHost'] + '-edge-iot-simulator'] + request_job['resource'], verify=False)
        if r.status_code == 200:
            print('Host ' + nodeName_host_dict[request_job['destinationHost'] + '-edge-iot-simulator'] + ' available with code ' + str(r.status_code))
        else:
            print('Host ' + nodeName_host_dict[request_job['destinationHost'] + '-edge-iot-simulator'] + ' NOT available with code ' + str(r.status_code))
            exit(1)
    
    client = connect_mqtt()
    client.loop_start()

    time.sleep(5)

    # publish requests
    seq = 0
    for request_job in request_jobs:
        mqtt_client_id = request_job['sourceHost'] + '-' + request_job['topic']
        topic = f'services/requestSvc/{mqtt_client_id}/jobs/create/req'
        created_request_job = RequestJob(nodeName_host_dict[request_job['destinationHost'] + '-edge-iot-simulator'], request_job['resource'], request_job['count'], request_job['recurrence'])
        client.publish(topic, created_request_job.to_json())
        print('Sent RequestJob ' + created_request_job.to_json() + ' to ' + topic)
        time.sleep(seq * 5)
        seq += 1

    client.loop_stop()