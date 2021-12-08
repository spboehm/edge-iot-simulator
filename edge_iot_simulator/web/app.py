import os
import json

import threading
import logging
from flask import Flask, render_template, redirect, url_for, request, Response
from werkzeug.serving import make_server
from core.temperature_svc import TemperatureUnits

from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, hash_password
from flask_security.models import fsqla_v2 as fsqla

logging.basicConfig(format='%(asctime)s %(module)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

class WebApp(threading.Thread):

    def __init__(self, publisher, temperature_svc, cpu_load_svc):
        threading.Thread.__init__(self)
        app = self.create_app(publisher, temperature_svc, cpu_load_svc)
        self.srv = make_server('0.0.0.0', 5000, app, ssl_context='adhoc')
        self.ctx = app.app_context()
        self.ctx.push()
        self.logger = logging.getLogger(__name__)

    def create_app(self, publisher, temperature_svc, cpu_load_svc):
        app = Flask(__name__)
        app.config['DEBUG'] = True

        # Generate a nice key using secrets.token_urlsafe()
        app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
        app.config['SECURITY_PASSWORD_SALT'] = os.getenv("FLASK_SECURITY_PASSWORD_SALT")

        # Use an in-memory db
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('FLASK_SQLITE_DB_PATH')
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
        }

        # Create database connection object
        db = SQLAlchemy(app)

        # Define models
        fsqla.FsModels.set_db_info(db)

        class Role(db.Model, fsqla.FsRoleMixin):
            pass

        class User(db.Model, fsqla.FsUserMixin):
            pass

        # Setup Flask-Security
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        security = Security(app, user_datastore)

        # Create a user to test with
        @app.before_first_request
        def create_user():
            db.create_all()
            if not user_datastore.find_user(email=os.getenv('FLASK_WEB_USER')):
                user_datastore.create_user(email=os.getenv('FLASK_WEB_USER'), password=hash_password(os.getenv('FLASK_WEB_PASSWORD')))
            db.session.commit()

        @app.route("/")
        @auth_required()
        def index():
            return render_template('dashboard.html', TemperatureMeasurement=temperature_svc.get_temperature(TemperatureUnits.celsius.name), MqttStatistics=publisher.get_mqtt_statistics())

        @app.route("/temperature")
        @auth_required()
        def get_temperature():
            return temperature_svc.get_temperature(TemperatureUnits.celsius.name).to_string()
        
        @app.route("/cpu-load", methods=["POST"])
        @auth_required()
        def create_cpu_load_job():
            form_data = request.form
            cpu_load_svc.create_cpu_load_job(int(form_data.get('duration')), float(form_data.get('target_load')))
            return redirect('/cpu-load')

        @app.route("/cpu-load", methods=["GET"])
        @auth_required()
        def get_cpu_load():
            return render_template('cpu-load.html', CPULoadJobHistory=cpu_load_svc.get_cpu_load_job_history())
        
        @app.route("/cpu-load/<id>", methods=["DELETE"])
        @auth_required()
        def terminate_cpu_load_job(id):
            # TODO: handle return
            cpu_load_svc.delete_cpu_load_job_by_id(id)
            return Response(status=200)

        @app.route("/device-info")
        def get_device_info():
            return json.dumps({"device-info": os.getenv('MQTT_CLIENT_ID')})

        return app

    def run(self):
        self.logger.info('Successfully started WebApp...')
        self.srv.serve_forever()

    def stop(self):
        self.logger.info('WebApp received shutdown signal....')
        self.srv.shutdown()
