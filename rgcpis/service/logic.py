# -*- coding: utf-8 -*-
import re
import pexpect
from rgcpis.service.forms import IPADDRESS_RE
import time
from flask_login import current_app
from rgcpis.service.models import MachineRecord, Service
from threading import Thread

IPMI_OFFSET = 8

STATUS = {1: 'on', 2: 'soft', 3: 'on'}


class GeneralError(Exception):
    def __init__(self, value, description):
        self.value = value
        self.description = description

    def __repr__(self):
        return "<{} {}：{}>".format(self.__class__.__name__, self.value, self.description)

    def __str__(self):
        return "<{} {}：{}>".format(self.__class__.__name__, self.value, self.description)


class NotExisted(GeneralError):
    def __init__(self, error_code='error', description=''):
        super(NotExisted, self).__init__(error_code, description)

    def __repr__(self):
        super(NotExisted, self).__repr__()

    def __str__(self):
        super(NotExisted, self).__str__()


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
        elif int(startips[-1]) > int(endips[-1]):
            return None, None
        else:
            return startips, endips


def thread_ssh(formt_ipmiip, option, option_ip=None):
    from manage import app
    IPMI_SECRET = {'17': {'username': 'root', 'password': 'root'}, '20': {'username': 'USERID', 'password': 'PASSW0RD'}}
    with app.app_context():
        results = []
        for ip_dict in formt_ipmiip:
            ips = ip_dict['real_ip'].split('.')[1]

            if ips == '17':
                ssh_add = 'ipmitool -H {ip} -U {username} -P {password} chassis power {option}'.format(
                    ip=ip_dict['ipmi_ip'], username=IPMI_SECRET[ips]['username'],
                    password=IPMI_SECRET[ips]['password'], option=option)
                chile = pexpect.spawn(ssh_add)
                while chile.isalive():
                    time.sleep(1)
                result = chile.read()
            else:
                if option != 'soft':
                    ipmi_guide = "ipmitool  -H {IPA} -U {username} -P {password} -I lanplus chassis bootdev pxe".format(
                        IPA=ip_dict['ipmi_ip'], username=IPMI_SECRET[ips]['username'],
                        password=IPMI_SECRET[ips]['password'])
                    guide = pexpect.spawn(ipmi_guide)
                    while guide.isalive():
                        time.sleep(1)
                    result = guide.read()
                ssh_add = 'ipmitool -H {IPA} -U {username} -P {password} -I lanplus chassis power {option}'.format(
                    IPA=ip_dict['ipmi_ip'], option=option, username=IPMI_SECRET[ips]['username'],
                    password=IPMI_SECRET[ips]['password'])
                print ssh_add
                chile = pexpect.spawn(ssh_add)
                while chile.isalive():
                    time.sleep(1)
                result = chile.read()
            results.append(result)
        return results


def thread_format_ip(ip):
    service = Service.query.filter_by(ip=ip).first()
    return {'real_ip': ip, 'ipmi_ip': service.get_ipmiip()}


def ssh_machine_shell(starts, ends=None, option=None, option_ip=None):
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
        service = service_last_options(service, option_ip)
        formt_ipmiip.append({'real_ip': ip, 'ipmi_ip': service.get_ipmiip()})
    thread = Thread(target=thread_ssh, args=(formt_ipmiip, option, option_ip))
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


def save_machinerecord_log(request_ip, operation, operation_ip):
    record = MachineRecord(request_ip, operation, operation_ip)
    record.save()


def service_last_options(service, ip):
    service.update_ip = ip
    return service.save()


def shutdown_server(ip, operator):
    import rpyc
    save_machinerecord_log(ip, '机器关机中', operator)
    c = rpyc.connect(ip, 60000)
    result = c.root.shutdown()
    if not result['status']:
        raise NotExisted(description=result['result'])
    return result['status']


def check_service_off(ip):
    while True:
        ipmat = thread_format_ip(ip)
        r = thread_ssh([ipmat], option='status')[0]
        # r = ssh_machine_shell(ip, option='status')[0]
        status = r.strip().split(' ')[-1]
        if status in ['off', 'on']:
            if status == 'on':
                time.sleep(3)
            else:
                save_machinerecord_log(ip, '机器已关机', ip)
                break


def zfx_without_result(ssh):
    current_app.logger.error(ssh)
    result = pexpect.spawn(ssh)
    message = result.read()
    if message:
        current_app.logger.error(message)
        raise NotExisted(description=message)


def start_disckless_reload(service, operation, version):
    thread = Thread(target=disckless_operation, args=(service, operation, version))
    thread.start()
    # disckless_operation(service, operation, version)


def disckless_operation(service, operation, version):
    from manage import app
    with app.app_context():
        operaction = {1: '重启', 0: '升级', 2: '备份母盘'}
        operact = operaction[service.iscsi_status]
        try:
            if service.iscsi_status == 99:
                raise NotExisted(description='机器操作已经被触发')
            service.iscsi_status = 99
            service.save()
            save_machinerecord_log(service.ip, '机器开始' + operact, service.update_ip)
            check_service_off(service.ip)
            zfx_without_result('tgt-admin --delete iqn.2016-08.renderg.com:{}'.format(service.ip))
            save_machinerecord_log(service.ip, '停止映射成功', service.ip)
            if operation != 'upload':
                zfx_without_result('zfs destroy storage/vh{}_{}'.format(service.version, service.ip))
                save_machinerecord_log(service.ip, '更新ZFS:删除原有卷成功', service.ip)
            else:
                zfx_without_result('zfs snapshot storage/{}'.format(version.description))
                save_machinerecord_log(service.ip, '备份建立快照成功', service.ip)
                service.status = 6
                service.save()
            zfx_without_result(
                'zfs clone storage/{description} storage/vh{version}_{ip}'.format(version=version.version,
                                                                                  description=version.description,
                                                                                  ip=service.ip))
            save_machinerecord_log(service.ip, '更新ZFS:克隆新卷成功', service.ip)
            tgt_conf = '<target iqn.2016-08.renderg.com:{ip}>\nbacking-store /dev/storage/vh{version}_{ip}\n</target>'.format(
                ip=service.ip, version=version.version)
            with open('/etc/tgt/conf.d/{}.conf'.format(service.ip), 'w+') as f:
                f.write(tgt_conf)
                f.close()
            save_machinerecord_log(service.ip, '更新配置文件成功', service.ip)
            zfx_without_result('tgt-admin --update iqn.2016-08.renderg.com:{}'.format(service.ip))
            save_machinerecord_log(service.ip, '更新tgt成功', service.ip)
            service.status = 1
            service.iscsi_status = 1
            service.version_id = version.id
            service.save()
            ssh_machine_shell(service.ip, option='on', option_ip=service.ip)
            save_machinerecord_log(service.ip, '机器' + operact + '成功,机器开机中', service.update_ip)
        except NotExisted as ne:
            current_app.logger.error(ne.description)
            save_machinerecord_log(service.ip, '机器' + operact + '失败:' + ne.description, service.ip)

# def disckless_backup(old_service, version_id):
#     shutdown_server(old_service.ip)
#     check_service_status(old_service.ip)
#     version = ServiceVersion.query.filter_by(id=version_id).first()
#     ssh = 'zfs clone storage/vh{version}_{description} storage/vh{new_version}_{ip}'.format(version=old_service.version,
#                                                                                             description=old_service.version_description,
#                                                                                             new_version=version.version,
#                                                                                             ip=old_service.ip)
#     result = pexpect.spawn(ssh)
#     if result.read():
#         raise NotExisted(description=result.read())
#     ssh = 'zfs snapshot storage/vh{}_{}'.format(version.version, version.version_description)
#     result = pexpect.spawn(ssh)
#     if result.read():
#         raise NotExisted(description=result.read())
#     old_service.status = 6
#     ssh_machine_shell(old_service.ip, option='on', option_ip=old_service.ip)
