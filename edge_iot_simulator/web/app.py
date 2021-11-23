import threading
import logging
from flask import Flask, render_template, redirect, url_for, request, Response
from werkzeug.serving import make_server
from core.temperature_svc import TemperatureUnits

logging.basicConfig(format='%(asctime)s %(module)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

class WebApp(threading.Thread):

    def __init__(self, publisher, temperature_svc, cpu_load_svc):
        threading.Thread.__init__(self)
        app = self.create_app(publisher, temperature_svc, cpu_load_svc)
        self.srv = make_server('0.0.0.0', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()
        self.logger = logging.getLogger(__name__)

    def create_app(self, publisher, temperature_svc, cpu_load_svc):
        app = Flask(__name__)

        @app.route("/")
        def index():
            return render_template('dashboard.html', TemperatureMeasurement=temperature_svc.get_temperature(TemperatureUnits.celsius.name), MqttStatistics=publisher.get_mqtt_statistics())

        @app.route("/temperature")
        def get_temperature():
            return temperature_svc.get_temperature(TemperatureUnits.celsius.name).to_string()
        
        @app.route("/cpu-load", methods=["POST"])
        def create_cpu_load_job():
            form_data = request.form
            cpu_load_svc.create_cpu_load_job(int(form_data.get('duration')), float(form_data.get('target_load')))
            return redirect('/cpu-load')

        @app.route("/cpu-load", methods=["GET"])
        def get_cpu_load():
            return render_template('cpu-load.html', CPULoadJobHistory=cpu_load_svc.get_cpu_load_job_history())
        
        @app.route("/cpu-load/<id>", methods=["DELETE"])
        def terminate_cpu_load_job(id):
            cpu_load_svc.delete_cpu_load_job_by_id(id)
            return Response(status=200)

        return app

    def run(self):
        self.logger.info('Successfully started WebApp...')
        self.srv.serve_forever()

    def stop(self):
        self.logger.info('WebApp received shutdown signal....')
        self.srv.shutdown()
