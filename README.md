# Edge-IoT Simulator

The following project contains a small edge-IoT simulator.

## Components and Architecture

Components:

* `core`: IoT device simulators, e.g., `temperature` simulator
* `messaging`: MQTT messaging components to send data to MQTT broker
* `web`: A small flask application which provides access to selected data provided by `core` and `messaging`.

Architecture:

```bash
web <-> core <-> queue <-> mqtt_client
```

* `web`: The web application has a reference to the core services (e.g., temperature) and has currently three endpoints:
  * `/`: Dashboard which shows the latest temperature value
  * `/temperature`: Returns the latest temperature value as json
  * `/cpu-load`: Returns a UI to manage CPU load jobs
* `core, queue, mqtt_client`: The core services (e.g., `temperature`, `cpu-load`) are decoupled from the `mqtt_client` by a shared memory `threadsafe` queue. The `mqtt_client` forwards the message with a corresponding topic and payload.

For example:

```bash

temperature <-> TemperatureMeasurement (timestamp=XXX,value=XXX,unit=XXX)
                            |
                            v
                MqttMessage(topic=sensors/id/data payload=TemperatureMeasurement)
                            |
                            v
                          queue
                            ^
                            |
                mqtt_client.client.publish(MqttMessage.topic, MqttMessage.payload)
```

Other available services follow the same decoupled architecture.

## Services

## TemperatureService (`core.temperature_svc.py`)

This service is continuously transmitting temperature values to an mqtt endpoint.

### HTTP-Endpoints

* (UI) `/` \[GET\]: Current temperature value
* (API) `/temperature` \[GET\]: Current temperature value as json

All of the endpoints are protected with login.
You can specify the initial user by defining `FLASK_WEB_USER` and `FLASK_WEB_PASSWORD` in the `env` file.
Just have a look at section *Run the project locally*.
By default, the web ui is running under `https://<<your-ip>>:5000`.
You need to accept the self-signed certificate in order to proceed.

### MQTT-Topics

**TemperatureMessage:** `sensors/<MQTT_CLIENT_ID>/data`

Payload:

```json
{
  "timestamp": 1637751270.438974, 
  "value": 33, 
  "unit": "celsius"
}
```

## CPULoadService (`core.cpu_load_svc`)

This service allow to stress the CPU of the edge device for a period of time.
It is possible to define the duration and the target load for the cpu.

For example, all logical cores can be utilized to run at 50% CPU utilization for 15min.

### HTTP_Endpoints

* (UI) `/cpu-load` \[GET\]: Allow to create new cpu load jobs and to manage already existing ones

### MQTT_TOPICS

**Request Creation of CPULoadJobAllCores:** `services/cpuLoadSvc/<MQTT_CLIENT_ID>/jobs/create/req`

Payload:

```json
{
  "duration": 200,
  "target_load": 0.50
}
```

**Response Creation of CPULoadJobAllCores:** `services/cpuLoadSvc/<MQTT_CLIENT_ID>/jobs/create/res`

On Success:

```json
{
  "success":{
    "duration":200,
    "target_load":0.5
  }
}
```

On Error:

```json
{
  "error": "Illegal message received: ('Duration must be between 30 and 3600',)"
}
```

**Request Reading all QueuedCPULoadJobAllCores:** `services/cpuLoadSvc/<MQTT_CLIENT_ID>/jobs/read/req`

Payload intentionally left blank.

**Response Reading all QueuedCPULoadJobAllCores:** `services/cpuLoadSvc/<MQTT_CLIENT_ID>/jobs/read/res`

```json
{
  "success":{
    "1":{
      "duration":60,
      "target_load":0.25,
      "id":1,
      "pid":30040,
      "state":"RUNNING"
    },
    "2":{
      "duration":60,
      "target_load":0.55,
      "id":2,
      "pid":null,
      "state":"CREATED"
    },
    "3":{
      "duration":60,
      "target_load":0.55,
      "id":3,
      "pid":null,
      "state":"CREATED"
    }
  }
}
```

**Request delete specific QueuedCPULoadJobAllCores:** `services/cpuLoadSvc/<MQTT_CLIENT_ID>/jobs/delete/req`

Payload:

```json
{
  "id":1
}
```

**Response delete specific QueuedCPULoadJobAllCores:** `services/cpuLoadSvc/<MQTT_CLIENT_ID>/jobs/delete/res`

```json
{
  "success":{
    "duration":200,
    "target_load":0.5,
    "id":4,
    "pid":13767,
    "state":"ABORTED"
  }
}
```

PLEASE NOTE:

* The **CPULoadService** is running a SQLite database to store the username and password for the web login.
* The submitted CPULoadJobs are only stored in-memory. That means, a shutdown of the application will lead to data loss. If you are restarting your application, you need recreate your job, respectively your job profile.

### General Information

All components can easily be configured with the following `.env` file with should be present in the root of this project.

```bash
# messaging
MQTT_SERVER_NAME=localhost
MQTT_PORT=1883
MQTT_TLS=False
MQTT_CA_CERTS=
MQTT_CERTFILE=
MQTT_KEYFILE=
MQTT_TLS_INSECURE=False
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_MAX_CONNECT_RETRIES=5
MQTT_RECONNECT_TIMEOUT=30
MQTT_CLIENT_ID=ab444537-cf67-47aa-a5ef-3548292e225b
MQTT_PUBLISH_QOS=2
MQTT_SUBSCRIBE_QOS=2
MQTT_TOPIC_PUBLISHER=publisher
MQTT_TOPIC_PUBLISHER_STATE=state

# core
MQTT_TOPIC_REQ_TYPE_CREATE=create/req
MQTT_TOPIC_RES_TYPE_CREATE=create/res
MQTT_TOPIC_REQ_TYPE_READ=read/req
MQTT_TOPIC_RES_TYPE_READ=read/res

## temperature
MQTT_TOPIC_SENSORS=sensors
MQTT_TOPIC_SENSORS_DATA=data

## cpu 
MQTT_TOPIC_SERVICES=services
MQTT_TOPIC_CPU_LOAD_SERVICE=cpuLoadSvc
MQTT_TOPIC_CPU_LOAD_SERVICE_DATA=jobs

CPU_LOAD_SVC_MIN_DURATION_SECONDS=30
CPU_LOAD_SVC_MAX_DURATION_SECONDS=3600

CPU_LOAD_SVC_MIN_TARGET_LOAD=0.25
CPU_LOAD_SVC_MAX_TARGET_LOAD=0.75

# web
WEB_HOSTNAME=localhost
FLASK_WEB_USER= # at least 4 characters
FLASK_WEB_PASSWORD= # at least 8 characters
FLASK_SECRET_KEY=
FLASK_SECURITY_PASSWORD_SALT=
FLASK_SQLITE_DB_PATH=sqlite:///../../flask-db.db

```

NOTE:

* Please make sure that you provide at least 4 characters for `FLASK_WEB_USER` and `FLASK_WEB_PASSWORD`.
* Furthermore, you can find additional information MQTT topic configuration in `settings.py`.

## Prerequisites

* Make sure that you installed `python3, python3-venv, python3-pip` on your system
* Make sure that you install `docker` on your system

## Run the project locally

* Install necessary packages: `sudo apt-get install python3-flask python3-venv python3-wheel`
* Clone/Pull this repository: `git clone https://gitlab.rz.uni-bamberg.de/sebastian.boehm/edge-iot-simulator`
* Go into the root directory of the repository, switch then to (`cd edge_iot_simulator`)
* Create the env file `.env` with the contents above and change the values according to your needs
* Go back to the root directory of the repository: `cd ..`
* Create a virtual environment: `python3 -m venv venv`
* Change to the virtual environment: `source venv/bin/activate`
* Update pip: `pip3 install --upgrade pip`
* Install the necessary dependencies: `pip3 install -r requirements.txt`
* Change the working directory: `cd edge_iot_simulator`
* Run:`python3 main.py`

You should see the following output:

```bash
11/11/2021 02:48:48 PM main Please any key to interrupt...
11/11/2021 02:48:48 PM mqtt_client Successfully started mqtt publisher...
11/11/2021 02:48:48 PM temperature_svc Successfully started temperature sensor...
11/11/2021 02:48:48 PM temperature_svc New value measured {"timestamp": 1636638528.2080338, "value": 26, "unit": "celsius"}
11/11/2021 02:48:48 PM app Successfully started WebbApp...
11/11/2021 02:48:48 PM mqtt_client Error establishing connection to localhost:1883[Errno 111] Connection refused
11/11/2021 02:48:48 PM mqtt_client mqtt publisher received shutdown signal
11/11/2021 02:48:51 PM temperature_svc New value measured {"timestamp": 1636638531.2109501, "value": 20, "unit": "celsius"}
11/11/2021 02:48:54 PM temperature_svc New value measured {"timestamp": 1636638534.2141488, "value": 7, "unit": "celsius"}
11/11/2021 02:48:57 PM temperature_svc New value measured {"timestamp": 1636638537.2166193, "value": 59, "unit": "celsius"}
11/11/2021 02:48:58 PM main Unknown error occurred: Could not establish the connection to the mqtt broker
11/11/2021 02:48:58 PM mqtt_client mqtt publisher received shutdown signal
11/11/2021 02:48:58 PM temperature_svc Temperature service received shutdown signal...
11/11/2021 02:48:58 PM app WebApp received shutdown signal....
11/11/2021 02:48:58 PM main Wait for graceful termination...
11/11/2021 02:49:00 PM main Successfully terminated edge-iot simulator
```

We can see the first measurements of the sensor. However, the edge-IoT simulator is terminating because no mqtt message broker is reachable.

For testing purposes, start a mqtt message broker via docker: `sudo docker run -d -p 1883:1883 -p 9001:9001 eclipse-mosquitto:1.6.15`

Run the application again: `python3 main.py`

You should see the following output:

```bash
11/11/2021 02:55:39 PM main Please any key to interrupt...
11/11/2021 02:55:39 PM mqtt_client Successfully started mqtt publisher...
11/11/2021 02:55:39 PM temperature_svc Successfully started temperature sensor...
11/11/2021 02:55:39 PM temperature_svc New value measured {"timestamp": 1636638939.4815965, "value": 46, "unit": "celsius"}
11/11/2021 02:55:39 PM app Successfully started WebbApp...
11/11/2021 02:55:39 PM mqtt_client Publisher connected with result code 0
11/11/2021 02:55:39 PM mqtt_client Successfully published message {"timestamp": 1636638939.4815965, "value": 46, "unit": "celsius"}
11/11/2021 02:55:42 PM temperature_svc New value measured {"timestamp": 1636638942.4844544, "value": 14, "unit": "celsius"}
11/11/2021 02:55:42 PM mqtt_client Successfully published message {"timestamp": 1636638942.4844544, "value": 14, "unit": "celsius"}
11/11/2021 02:55:45 PM temperature_svc New value measured {"timestamp": 1636638945.4878645, "value": 36, "unit": "celsius"}
11/11/2021 02:55:45 PM mqtt_client Successfully published message {"timestamp": 1636638945.4878645, "value": 36, "unit": "celsius"}
^C11/11/2021 02:55:48 PM main Received user's shutdown signal...
11/11/2021 02:55:48 PM mqtt_client mqtt publisher received shutdown signal
11/11/2021 02:55:48 PM temperature_svc New value measured {"timestamp": 1636638948.4884603, "value": 1, "unit": "celsius"}
11/11/2021 02:55:48 PM mqtt_client Successfully published message {"timestamp": 1636638948.4884603, "value": 1, "unit": "celsius"}
11/11/2021 02:55:48 PM mqtt_client mqtt publisher received shutdown signal
11/11/2021 02:55:48 PM temperature_svc Temperature service received shutdown signal...
11/11/2021 02:55:48 PM app WebApp received shutdown signal....
11/11/2021 02:55:48 PM main Wait for graceful termination...
11/11/2021 02:55:51 PM main Successfully terminated edge-iot simulator
```

Now the edge-IoT simulator is connected to the local mqtt message broker.
Press `CTRL+C` to abort the program.

Network architecture:

```bash
-----------------------localhost----------------------
edge-IoT simulator <-> docker daemon <-> mqtt message broker
------------------------------------------------------
```

By default web application is available under `https://<your ip>:5000`.
Since the web application contains a self-signed certificate, you need to accept this certificate in your browser.

## Run with docker

To run edge-IoT simulator with docker, do the following:

* Change to the root directory of this repository
* Build the image: `sudo docker build -t edge-iot-simulator:1.0 .`
* Change the working directory to the directory: `cd edge_iot_simulator`
* Create and adjust the `.env` file! **Make sure that you take the right IP address for the message broker. If you are running the mqtt broker on the same system (physical host), obtain the broker's ip address via `sudo docker inspect <containername>`**.
* Run the image: `sudo docker run -p 5000:5000 --env-file=.env edge-iot-simulator:1.0`, choose `sudo docker run -d -p 5000:5000 --env-file=.env edge-iot-simulator:1.0`

```bash
-----------------------localhost----------------------
docker daemon <-> edge-IoT-simulator <-> mqtt message broker 
------------------------------------------------------
```
