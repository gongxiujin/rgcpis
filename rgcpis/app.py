# -*- coding: utf-8 -*-
from rgcpis.extensions import db, migrate
from flask import Flask
from flask import redirect, url_for
from rgcpis.service.logic import get_service_status, order_status
from rgcpis.service.views import service
import logging
import os, time
from sqlalchemy.engine import Engine
from sqlalchemy import event


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object('rgcpis.config.default.DefaultConfig')
    app.config.from_object(config)
    migrate.init_app(app, db)
    db.init_app(app)
    configure_logging(app)
    register_buleprint(app)
    configure_template_filters(app)

    @app.route('/')
    def first_program():
        return redirect(url_for('service.index'))

    return app


def register_buleprint(app):
    app.register_blueprint(service, url_prefix=app.config["SERVICE_URL"])


def configure_template_filters(app):
    app.jinja_env.filters['service_status'] = get_service_status
    app.jinja_env.filters['order_status'] = order_status


def configure_logging(app):
    logs_folder = os.path.join(app.root_path, os.pardir, "logs")
    from logging.handlers import SMTPHandler
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')

    info_log = os.path.join(logs_folder, app.config['INFO_LOG'])

    info_file_handler = logging.handlers.RotatingFileHandler(
        info_log,
        maxBytes=100000,
        backupCount=10
    )

    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(formatter)
    app.logger.addHandler(info_file_handler)

    error_log = os.path.join(logs_folder, app.config['ERROR_LOG'])

    error_file_handler = logging.handlers.RotatingFileHandler(
        error_log,
        maxBytes=100000,
        backupCount=10
    )

    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    app.logger.addHandler(error_file_handler)

    app.logger.info('start')
    app.logger.error('start')
