# -*- coding: utf-8 -*-
from rgcpis.user.views import users
from rgcpis.extensions import db, migrate, login_manager, csrf
from flask import Flask
from flask import redirect, url_for
from rgcpis.service.logic import get_service_status, order_status
from rgcpis.service.views import service
from rgcpis.user.models import User


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object('rgcpis.config.default.DefaultConfig')
    app.config.from_object(config)
    migrate.init_app(app, db)
    csrf.init_app(app)
    db.init_app(app)
    configure_extensions(app)
    register_buleprint(app)
    configure_template_filters(app)

    @app.route('/')
    def first_program():
        # return redirect(url_for('service.index'))
        return redirect(url_for('users.login'))

    return app


def configure_extensions(app):
    login_manager.login_view = app.config["LOGIN_VIEW"]
    login_manager.refresh_view = app.config["REAUTH_VIEW"]

    @login_manager.user_loader
    def load_user(user_id):
        """Loads the user. Required by the `login` extension."""
        u = User.query.filter_by(id=user_id).first()
        if u:
            user = u
            return user
        else:
            return None

    login_manager.init_app(app)


def register_buleprint(app):
    app.register_blueprint(service, url_prefix=app.config["SERVICE_URL"])
    app.register_blueprint(users, url_prefix=app.config["USER_URL"])


def configure_template_filters(app):
    app.jinja_env.filters['service_status'] = get_service_status
    app.jinja_env.filters['order_status'] = order_status
