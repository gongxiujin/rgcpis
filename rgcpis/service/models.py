# -*- coding: utf-8 -*-
from rgcpis.extensions import db
from datetime import datetime


class Service(db.Model):
    __tablename__ = "service"

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), nullable=False, index=True)
    ip_mac = db.Column(db.String(30)) #nullable=False, index=True
    ipmi_ip = db.Column(db.String(15), nullable=False)
    ipmi_ip_mac = db.Column(db.String(30))
    date_joined = db.Column(db.DateTime, default=datetime.now())
    last_update = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(db.Integer, default=0, nullable=True)  # 0关机  1开机  2重装前引导 3重装中  4备份前引导 5  上传版本中 6 安装完毕重启中
    iscsi_status = db.Column(db.Integer, default=1, nullable=True)
    version_id = db.Column(db.ForeignKey('service_version.id'), nullable=True)
    cluster_id = db.Column(db.Integer(), db.ForeignKey("service_cluster.id"))
    cluster = db.relationship("Cluster", backref=db.backref('cluster', lazy='dynamic'), uselist=False)
    update_ip = db.Column(db.String(15))

    def __init__(self, ip, iscsi_status=None, cluster_id=2):
        self.ip = ip
        self.status = 0
        self.cluster_id=cluster_id
        if iscsi_status:
            self.iscsi_status = iscsi_status
        self.date_joined = datetime.now()

    def set_ipmiip(self, offset):
        ipmips = []
        ips = self.ip.split('.')
        ips[-2] = str(int(ips[-2]) + int(offset))
        for i in ips:
            ipmips.append(i.zfill(3))
        self.ipmi_ip = '.'.join(ipmips)

    def set_version(self, version_num):
        version = ServiceVersion.query.filter_by(version=version_num).first()
        if version:
            self.version_id = version.id

    def get_ipmiip(self):
        ipmi_ips = [str(int(s)) for s in self.ipmi_ip.split('.')]
        return '.'.join(ipmi_ips)

    @property
    def version(self):
        if self.version_id:
            version = ServiceVersion.query.filter_by(id=self.version_id).first()
            return version.version
        else:
            return None

    @property
    def version_description(self):
        if self.version_id:
            version = ServiceVersion.query.filter_by(id=self.version_id).first()
            return version.description
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
        return self


class MachineRecord(db.Model):
    __tablename__ = 'machine_record'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), nullable=False)
    result = db.Column(db.Text(), nullable=False)
    create_time = db.Column(db.DateTime(), default=datetime.now())
    option_ip = db.Column(db.String(21))

    def __init__(self, ip, result, option_ip):
        self.ip = ip
        self.result = result
        self.create_time = datetime.now()
        self.option_ip = option_ip

    def save(self):
        db.session.add(self)
        db.session.commit()


class ServiceVersion(db.Model):
    __tablename__ = "service_version"

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(30), nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=False)
    type = db.Column(db.Integer, default=1) # 1  ipxe   2  disckless
    create_time = db.Column(db.DateTime(), default=datetime.now())

    def __init__(self, version, description, type=1):
        self.version = version
        self.description = description
        self.type = type
        self.create_time = datetime.now()

    @classmethod
    def get_version_id(cls, version):
        versions = cls.query.filter_by(version=version).first()
        return versions.id if versions else None

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

class Cluster(db.Model):
    __tablename__ = "service_cluster"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False, unique=True)
    description = db.Column(db.String(255))
    create_time = db.Column(db.DateTime(), default=datetime.now())