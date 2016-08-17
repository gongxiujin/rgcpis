# -*- coding: utf-8 -*-
import re
import pexpect
from rgcpis.service.forms import IPADDRESS_RE
import time
from flask_login import current_app
from rgcpis.service.models import MachineRecord, Service
from threading import Thread

IPMI_OFFSET = 8


def validate_ipaddress(startip, endip):
    startre = re.match(IPADDRESS_RE, startip)
    endre = re.match(IPADDRESS_RE, endip)
    if not startre or not endre:
        return None, None
    if startip and endip:
        startips = [s for s in startip.split('.')]
        endips = [e for e in endip.split('.')]
        if startips[0] != endips[0] or startips[1] != endips[1] or startips[2] != endips[2]:
            return None, None
        elif startips[-1] > endips[-1]:
            return None, None
        else:
            return startips, endips


def thread_ssh(formt_ipmiip, option):
    from manage import app
    with app.app_context():
        for ip_dict in formt_ipmiip:
            ssh_add = 'ipmitool -H {IPA} -U USERID -P PASSW0RD -I lanplus chassis power {option}'.format(
                IPA=ip_dict['ipmi_ip'], option=option)

            chile = pexpect.spawn(ssh_add)
            while chile.isalive():
                time.sleep(1)
            result = chile.read()
            record = MachineRecord(ip_dict['real_ip'], result)
            record.save()


def ssh_machine_shell(starts, ends=None, option=None):
    ips = []
    formt_ipmiip = []
    if not ends:
        ips = [starts]
    else:
        iprange = xrange(int(starts[-1]), int(ends[-1]) + 1)
        for i in iprange:
            starts[-1] = str(i)
            ips.append('.'.join(starts))
    for ip in ips:
        service = Service.query.filter_by(ip=ip).first()
        formt_ipmiip.append({'real_ip': ip, 'ipmi_ip': service.get_ipmiip()})
    thread = Thread(target=thread_ssh, args=(formt_ipmiip, option))
    thread.start()
    # thread_ssh(formt_ipmiip, option)


def get_diffence_set_ips(result, startip, endip):
    startips = [i for i in startip.split('.')]
    endips = [s for s in endip.split('.')]
    diffence = []
    if len(result) == int(endips[-1]) - int(startips[-1]) + 1:
        return []
    range_service = xrange(int(startips[-1]), int(endips[-1]) + 1)
    for i in range_service:
        startips[-1] = str(i)
        ip = '.'.join(startips)
        if ip not in result:
            diffence.append(ip)
    return diffence


def ssh_query_activity_machine():
    from manage import app
    print 'start'
    with app.app_context():
        all_ips = current_app.config['SERVICE_MACHINE_IP']
        activity_services = []
        print 'before find'
        for ip_content in all_ips.keys():
            ssh_query = 'fping -a -g {ipstart} {ipend}'.format(ipstart=all_ips[ip_content][0],
                                                               ipend=all_ips[ip_content][1])
            result = pexpect.spawn(ssh_query)
            print 'before while'
            while result.isalive():
                print 'in while'
                time.sleep(2)
            result = result.read().strip().split('\r\n')
            activity_services += result
        print activity_services
        services = Service.query.all()
        for service in services:
            if service.ip in activity_services:
                service.status = 1
            else:
                service.status = 0
            service.save()
        print 'end one'


def init_service_machines():
    print 'start'
    services = current_app.config['SERVICE_MACHINE_IP']
    for ip in services:
        startips = services[ip][0].split('.')
        iprange = xrange(int(startips[-1]), int(services[ip][1].split('.')[-1]) + 1)
        for i in iprange:
            startips[-1] = str(i)
            query_ip = '.'.join(startips)
            querys = Service.query.filter_by(ip=query_ip).first()
            if not querys:
                new_service = Service(query_ip)
                new_service.save()
    print 'over'


def get_service_status(status):
    return current_app.config['SERVICE_STATUS'][status]


def order_status(order):
    return int(not order)


def check_service(service):
    if service.status not in [0, 1]:
        return False
    return True


def service_last_options(service, ip):
    service.last_update = ip
    return service.save()


def upload_machine_options(service, version):
    pass
