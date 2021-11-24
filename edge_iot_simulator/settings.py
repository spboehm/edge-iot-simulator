import os
from dotenv import load_dotenv
load_dotenv()

topic_cpuLoadSvc_cpuLoadJob_create_req = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_REQ_TYPE_CREATE')])
topic_cpuLoadSvc_cpuLoadJob_read_req = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_REQ_TYPE_READ')])
topic_cpuLoadSvc_cpuLoadJob_read_res = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_RES_TYPE_READ')])
