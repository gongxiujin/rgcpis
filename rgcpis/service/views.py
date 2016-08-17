# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash
from rgcpis.extensions import csrf
from flask_login import current_app, login_required, current_user
from flask_login import request
from rgcpis.service.logic import validate_ipaddress, ssh_machine_shell, upload_machine_options, \
    service_last_options
from rgcpis.service.models import Service, MachineRecord, ServiceVersion
from rgcpis.utils.auth import json_response, response_file

service = Blueprint('service', __name__)
COPAY_PER_PAGE = 20
ORDER_STATUS = {1: 'desc', 0: 'asc'}
VERSION_RE = r'(\d{0,3}\.){1,2}(\d{0,3})'


@service.route('/')
@login_required
def index():
    if current_user is None and not current_user.is_authenticated:
        return redirect(url_for("users.login"))

    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', type=int)
    ip = request.args.get('ip', type=int)
    versions = ServiceVersion.query.all()
    order_by = []
    if status is not None:
        order_by.append('status ' + ORDER_STATUS[status])
    if ip is not None:
        order_by.append('ipmi_ip ' + ORDER_STATUS[ip])
    services = Service.query.order_by(*order_by).paginate(page, COPAY_PER_PAGE, False)
    return render_template('auth/index.html', services=services, status=status, ip=ip, versions=versions)


@service.route('/machine_option', methods=['POST'])
@csrf.exempt
def machine_option():
    if request.method == 'POST':
        ipstart = request.form.get('ipstart')
        ipend = request.form.get('ipend')
        option = request.form.get('option')
        ipstarts, ipends = validate_ipaddress(ipstart, ipend)
        if not ipstarts and not ipends:
            flash(u'请检查IP格式', 'danger')
            return redirect(url_for('service.index'))
        ssh_machine_shell(ipstarts, ipends, option)
        flash(u'操作成功请稍后刷新页面查看结果', 'success')
        return redirect(url_for('service.index'))


@service.route('/single_service_option/<string:options>/<int:service_id>')
def single_service_option(options, service_id):
    service = Service.query.filter_by(id=service_id).first()
    if service.status == 0 and options == "shutdown":
        flash(u"机器已经关机", "danger")
    if service.status == 2 and options == "restart":
        flash(u"已经在重启中", "danger")
    if service.status == 1 and options == 'start':
        flash(u"已经开机", "danger")
    else:
        ssh_machine_shell(service.ip, option=options)
        flash(u'重启成功', "success")
    return redirect(request.referrer)


@service.route('/service_upload/<int:service_id>', methods=["POST"])
def service_upload(service_id):
    import re
    version = request.form.get("new_version")
    mach = re.match(VERSION_RE, version)
    if not mach:
        flash(u'版本号格式错误', 'danger')
    description = request.form.get("description")
    service_version = ServiceVersion.query.filter_by(version=version).first()
    if service_version:
        flash(u'版本号已存在', 'danger')
        return redirect(request.referrer)
    if version and description:
        service_version = ServiceVersion(version, description)
        service_version = service_version.save()
        service = Service.query.filter_by(id=service_id).first_or_404()
        service = service_last_options(service, request.remote_addr)
        service.version_id = service_version.id
        service.status = 4
        service = service.save()
        ssh_machine_shell(service.ip, option='reset')
        flash(u'版本上传中，请稍后', 'success')
        return redirect(request.referrer)
    return redirect(request.referrer)


@service.route('/echo_machine_record')
def echolog():
    records = MachineRecord.query.order_by(MachineRecord.id.desc()).all()
    return render_template('auth/echo_log.html', records=records)


@service.route('/renew_services', methods=['POST'])
@login_required
@csrf.exempt
def renew_services():
    try:
        version = request.form.get('version', type=int)
        option = request.form.get('option')
        ids = request.form.getlist('service_id', type=int)
        for service_id in ids:
            service = Service.query.filter_by(id=service_id).first_or_404()
            service = service_last_options(service, request.remote_addr)
            service.status = 2
            service.version_id = version
            service = service.save()
            if option == 'now':
                flash(u'机器正在重装中，请注意日志', 'success')
                ssh_machine_shell(service.ip, option='reset')
            else:
                flash(u'机器将在下次重启时重装，请注意查看日志', 'success')
        return redirect(request.referrer)
    except Exception as e:
        current_app.logger.error('error in renew service')
        current_app.logger.error(e)
        return redirect(request.referrer)


@service.route("/check_start_status/aoe.ipxe")
def get_service_status():
    request_ip = request.remote_addr
    service = Service.query.filter_by(ip=request_ip).first()
    if not service:
        return json_response(1, error_msg='error')
    filename = 'aoe.ipxe'
    if service.status in [2, 4]:
        record = MachineRecord(service.ip, u'机器引导中')
        record.save()
        configs = current_app.config['DHCP_NETWORK_START']
    else:
        configs = current_app.config['BOOT_START']
        service.status = 1
        service.save()
    return response_file(data=configs, filename=filename)


@service.route("/service_config_file/install.bat")
def service_config_file():
    request_ip = request.remote_addr
    service = Service.query.filter_by(ip=request_ip).first()
    if not service:
        current_app.logger.error(request_ip+'not in service')
        return json_response(1)
    filename = 'install.bat'
    configs = ''
    if service.status in [2, 3]:
        service.status = 3
        service.save()
        record = MachineRecord(service.ip, u'开始重装系统')
        record.save()
        configs = current_app.config['RENEW_SERVICE'].format(version=service.version)
    elif service.status in [4, 5]:
        service.status = 5
        service.save()
        record = MachineRecord(service.ip, u'开始备份系统')
        record.save()
        configs = current_app.config['UPLOAD_SERVICE'].format(version=service.version)
    return response_file(data=configs, filename=filename)


@service.route("/notification_service_status/")
def notification_service_status():
    request_ip = request.remote_addr
    service = Service.query.filter_by(ip=request_ip).first()
    if not service:
        current_app.logger.error(request_ip+'not in service')
        return json_response(1)
    if service.status == 3:
        result = u'系统重装完成,准备开机'
    if service.status == 5:
        result = u'系统备份完成,准备开机'
    else:
        result = u'操作完成,准备开机'
    record = MachineRecord(service.ip, result)
    record.save()
    service.status = 6
    service.save()
    return json_response(0)


@service.route("/service_start/")
def service_start():
    request_ip = request.remote_addr
    service = Service.query.filter_by(ip=request_ip).first()
    if not service:
        current_app.logger.error(request_ip+'not in service')
        return json_response(1)
    service.status = 1
    service.save()
    return json_response(0)
