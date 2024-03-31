import os
from dotenv import load_dotenv
load_dotenv()

# temperature_svc
topic_temperatureSvc_temperature_data = os.getenv('CUSTOM_TOPIC_TEMPERATURESVC_TEMPERATURE_DATA') 
if topic_temperatureSvc_temperature_data is None or len(topic_temperatureSvc_temperature_data) < 1:
    topic_temperatureSvc_temperature_data = "/".join([os.getenv('MQTT_TOPIC_SENSORS'), os.getenv('MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_SENSORS_DATA')])

# cpu_load_svc
topic_cpuLoadSvc_cpuLoadJob_create_req = os.getenv('CUSTOM_TOPIC_CPULOADSVC_CPULOADJOB_CREATE_REQ')
if topic_cpuLoadSvc_cpuLoadJob_create_req is None or len(topic_cpuLoadSvc_cpuLoadJob_create_req) < 1:
    topic_cpuLoadSvc_cpuLoadJob_create_req = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_REQ_TYPE_CREATE')])

topic_cpuLoadSvc_cpuLoadJob_create_res = os.getenv('CUSTOM_TOPIC_CPULOADSVC_CPULOADJOB_CREATE_RES')
if topic_cpuLoadSvc_cpuLoadJob_create_res is None or len(topic_cpuLoadSvc_cpuLoadJob_create_res) < 1:
    topic_cpuLoadSvc_cpuLoadJob_create_res = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_RES_TYPE_CREATE')])

topic_cpuLoadSvc_cpuLoadJob_read_req = os.getenv('CUSTOM_TOPIC_CPULOADSVC_CPULOADJOB_READ_REQ')
if topic_cpuLoadSvc_cpuLoadJob_read_req is None or len(topic_cpuLoadSvc_cpuLoadJob_read_req) < 1:
    topic_cpuLoadSvc_cpuLoadJob_read_req = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_REQ_TYPE_READ')])

topic_cpuLoadSvc_cpuLoadJob_read_res = os.getenv('CUSTOM_TOPIC_CPULOADSVC_CPULOADJOB_READ_RES')
if topic_cpuLoadSvc_cpuLoadJob_read_res is None or len(topic_cpuLoadSvc_cpuLoadJob_read_res) < 1:
    topic_cpuLoadSvc_cpuLoadJob_read_res = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_RES_TYPE_READ')])

topic_cpuLoadSvc_cpuLoadJob_delete_req = os.getenv('CUSTOM_TOPIC_CPULOADSVC_CPULOADJOB_DELETE_REQ')
if topic_cpuLoadSvc_cpuLoadJob_delete_req is None or len(topic_cpuLoadSvc_cpuLoadJob_delete_req) < 1:
    topic_cpuLoadSvc_cpuLoadJob_delete_req = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_REQ_TYPE_DELETE')])

topic_cpuLoadSvc_cpuLoadJob_delete_res = os.getenv('CUSTOM_TOPIC_CPULOADSVC_CPULOADJOB_DELETE_RES')
if topic_cpuLoadSvc_cpuLoadJob_delete_res is None or len(topic_cpuLoadSvc_cpuLoadJob_delete_res) < 1:
    topic_cpuLoadSvc_cpuLoadJob_delete_res = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_RES_TYPE_DELETE')])

# request_svc
topic_requestSvc_requestJob_create_req = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_REQUEST_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_REQUEST_SERVICE_DATA'), os.getenv('MQTT_TOPIC_REQ_TYPE_CREATE')])

topic_requestSvc_requestJob_create_res = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_REQUEST_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_REQUEST_SERVICE_DATA'), os.getenv('MQTT_TOPIC_RES_TYPE_CREATE')])

# mqtt_client
topic_mqtt_client_publisher_state = os.getenv('CUSTOM_MQTT_CLIENT_PUBLISHER_STATE')
if topic_mqtt_client_publisher_state is None or len(topic_mqtt_client_publisher_state) < 1:
    topic_mqtt_client_publisher_state = "/".join([os.getenv('MQTT_TOPIC_PUBLISHER'), os.getenv('MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_PUBLISHER_STATE')])
