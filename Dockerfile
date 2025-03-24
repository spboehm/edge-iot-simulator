FROM python:3.8.12-slim-bullseye

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN python3 -m pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . . 
RUN cp ./edge_iot_simulator/.env-example ./edge_iot_simulator/.env

EXPOSE 8087

CMD [ "python", "./edge_iot_simulator/main.py" ]