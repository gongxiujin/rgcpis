# -*- coding: utf-8 -*-
from rgcpis.extensions import db
from datetime import datetime


class Service(db.Model):
    __tablename__ = "service"

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), nullable=False)
    ip_mac = db.Column(db.String(30))
    ipmi_ip = db.Column(db.String(15), nullable=False)
    ipmi_ip_mac = db.Column(db.String(30))
    date_joined = db.Column(db.DateTime, default=datetime.now())
    last_update = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(db.Integer, default=0, nullable=True)
    version_id = db.Column(db.ForeignKey('service_version.id'), nullable=True)
    update_ip = db.Column(db.String(15))

    def __init__(self, ip):
        self.ip = ip
        self.status = 0
        self.date_joined = datetime.now()

    def set_ipmiip(self, offset):
        ipmips = []
        ips = self.ip.split('.')
        ips[-2] = str(int(ips[-2]) + int(offset))
        for i in ips:
            ipmips.append(i.zfill(3))
        self.ipmi_ip = '.'.join(ipmips)

    def get_ipmiip(self):
        ipmi_ips = [str(int(s)) for s in self.ipmi_ip.split('.')]
        return '.'.join(ipmi_ips)

    @property
    def version(self):
        if self.version_id:
            service = ServiceVersion.query.filter_by(id=self.version_id).first()
            return service.version
        else:
            return None

    @staticmethod
    def get_ipmiips(realips):
        result = []
        for ip in realips:
            service = Service.query.filter_by(ip=ip).first()
            ipmi_ips = [str(int(s)) for s in service.ipmi_ip.split('.')]
            result.append('.'.join(ipmi_ips))
        return result

    def save(self):
        db.session.add(self)
        db.session.commit()


class MachineRecord(db.Model):
    __tablename__ = 'machine_record'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), nullable=False)
    result = db.Column(db.Text(), nullable=False)

    def __init__(self, ip, result):
        self.ip = ip
        self.result = result

    def save(self):
        db.session.add(self)
        db.session.commit()


class ServiceVersion(db.Model):
    __tablename__ = "service_version"

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(30), nullable=False)
    create_time = db.Column(db.DateTime(), default=datetime.now())

    def __init__(self, version):
        self.version = version
        self.create_time = datetime.now()

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
