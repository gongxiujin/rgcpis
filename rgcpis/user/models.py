# -*- coding: utf-8 -*-
from flask_login import UserMixin, AnonymousUserMixin, current_app
from rgcpis.extensions import db
from datetime import datetime
import hashlib


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(191), unique=True, nullable=False, index=True)
    # nickname = db.Column(db.String(191), nullable=False, index=True)
    _password = db.Column('password', db.String(120), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.now())
    lastseen = db.Column(db.DateTime, default=datetime.now())
    lastip = db.Column(db.String(16), nullable=True)
    update_ip = db.Column(db.String(16), nullable=True)
    update_date = db.Column(db.DateTime, default=datetime.now())

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = self._encryption_password(password)

    def _encryption_password(self, password):
        return hashlib.md5(hashlib.md5(password).hexdigest() + current_app.config['SECRET_SALT']).hexdigest()

    def check_password(self, password):
        if self.password is None:
            return False
        return self.password == self._encryption_password(password)

    password = db.synonym('_password',
                          descriptor=property(_get_password,
                                              _set_password))

    @classmethod
    def authenticate(cls, login, password):
        user = cls.query.filter(User.username == login).first()

        if user:
            authenticated = user.check_password(password)
        else:
            authenticated = False
        return user, authenticated

    def save(self):
        db.session.add(self)
        db.session.commit()

# class Group(db.Model):
#     __tablename__ = "groups"
#
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), unique=True, nullable=False)
#     description = db.Column(db.Text)
#
#     # Group types
#     admin = db.Column(db.Boolean, default=False, nullable=False)
#     guest = db.Column(db.Boolean, default=False, nullable=False)
#     banned = db.Column(db.Boolean, default=False, nullable=False)
