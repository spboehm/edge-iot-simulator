import os
from dotenv import load_dotenv
load_dotenv()

create_cpu_load_svc_req_topic = "/".join([os.getenv('MQTT_TOPIC_SERVICES'),os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'),os.getenv('MQTT_CLIENT_ID'),os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'),os.getenv('MQTT_TOPIC_REQ_TYPE_CREATE')])
read_cpu_load_svc_req_topic = "/".join([os.getenv('MQTT_TOPIC_SERVICES'),os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'),os.getenv('MQTT_CLIENT_ID'),os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'),os.getenv('MQTT_TOPIC_REQ_TYPE_READ')])
read_cpu_load_svc_res_topic = "/".join([os.getenv('MQTT_TOPIC_SERVICES'),os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE'),os.getenv('MQTT_CLIENT_ID'),os.getenv('MQTT_TOPIC_CPU_LOAD_SERVICE_DATA'),os.getenv('MQTT_TOPIC_RES_TYPE_READ')])
