# -*- coding: utf-8 -*-
from rgcpis.extensions import db, migrate
from flask import Flask
from flask import redirect, url_for
from rgcpis.service.logic import get_service_status, order_status
from rgcpis.service.views import service


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object('rgcpis.config.default.DefaultConfig')
    app.config.from_object(config)
    migrate.init_app(app, db)
    db.init_app(app)
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
