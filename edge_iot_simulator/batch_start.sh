#!/bin/sh
WEB_PORT=8087 MQTT_CLIENT_ID=fog-1-edge-iot-simulator python3 main.py &
WEB_PORT=8088 MQTT_CLIENT_ID=fog-2-edge-iot-simulator python3 main.py &
WEB_PORT=8089 MQTT_CLIENT_ID=fog-3-edge-iot-simulator python3 main.py &
WEB_PORT=8090 MQTT_CLIENT_ID=fog-4-edge-iot-simulator python3 main.py &
