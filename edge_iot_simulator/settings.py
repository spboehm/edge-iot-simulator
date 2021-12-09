import os
from dotenv import load_dotenv
load_dotenv()

# temperature_svc
topic_temperatureSvc_temperature_data = "/".join([os.getenv('MQTT_TOPIC_SENSORS'), os.getenv('MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_SENSORS_DATA')])

# cpu_load_svc
topic_cpuLoadSvc_cpuLoadJob_create_req = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_REQ_TYPE_CREATE')])
topic_cpuLoadSvc_cpuLoadJob_create_res = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_RES_TYPE_CREATE')])
topic_cpuLoadSvc_cpuLoadJob_read_req = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_REQ_TYPE_READ')])
topic_cpuLoadSvc_cpuLoadJob_read_res = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_RES_TYPE_READ')])
topic_cpuLoadSvc_cpuLoadJob_delete_req = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_REQ_TYPE_DELETE')])
topic_cpuLoadSvc_cpuLoadJob_delete_res = "/".join([os.getenv('MQTT_TOPIC_SERVICES'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'), os.getenv(
    'MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'), os.getenv('MQTT_TOPIC_RES_TYPE_DELETE')])

# mqtt_client
topic_mqtt_client_publisher_state = "/".join([os.getenv('MQTT_TOPIC_PUBLISHER'), os.getenv('MQTT_CLIENT_ID'), os.getenv('MQTT_TOPIC_PUBLISHER_STATE')])
