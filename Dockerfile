FROM python:3.8.12

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . . 

EXPOSE 8087

CMD [ "python", "./edge_iot_simulator/main.py" ]