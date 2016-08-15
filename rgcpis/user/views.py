# -*- coding: utf-8 -*-
from flask_login import current_user, login_user, logout_user, session
from flask import redirect, url_for, flash, render_template, Blueprint, request
from rgcpis.user.models import User
from rgcpis.user.forms import LoginForm
from rgcpis.utils.decorator import update_current_and_lastip

users = Blueprint('users', __name__)


@users.route("/login", methods=["GET", "POST"])
@update_current_and_lastip
def login():
    """
    Logs the user in
    """
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for("service.index"))

    form = LoginForm(request.form)
    if form.validate_on_submit():
        user, authenticated = User.authenticate(form.login.data,
                                                form.password.data)

        if user and authenticated:
            session['remember_me'] = "true"
            login_user(user, remember=form.remember_me.data)
            return redirect(request.args.get('next') or url_for("service.index"))

        flash("Wrong Username or Password.", "danger")
    return render_template("auth/login.html", form=form)


@users.route("/logout")
def logout():
    """
    Logs the user in
    """
    logout_user()

    return redirect(url_for('users.login'))
