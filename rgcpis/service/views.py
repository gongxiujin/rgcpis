# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash
from rgcpis.extensions import csrf
from flask_login import current_app, login_required, current_user
from flask_login import request
from rgcpis.service.forms import SearchServiceForm, AddMachineForm
from rgcpis.service.logic import validate_ipaddress, ssh_machine_shell, \
    service_last_options, start_disckless_reload, shutdown_server, start_disckless_backup, save_machinerecord_log, \
    NotExisted
from rgcpis.service.models import Service, MachineRecord, ServiceVersion
from rgcpis.utils.auth import json_response, response_file
from rgcpis.utils.decorator import check_ipxe_status, api_check_ipxe_status

service = Blueprint('service', __name__)
COPAY_PER_PAGE = 20
ORDER_STATUS = {1: 'desc', 0: 'asc'}
VERSION_RE = r'(\d{0,3}\.){1,2}(\d{0,3})'


@service.route('/', methods=['POST', 'GET'])
@login_required
def index():
    if current_user is None and not current_user.is_authenticated:
        return redirect(url_for("users.login"))

    page = request.args.get('page', 1, type=int)
    pageset = request.args.get('pageset', 25, type=int)
    status = request.args.get('status', type=int)
    ip = request.args.get('ip', type=int)
    order_by = []
    if status is not None:
        order_by.append('status ' + ORDER_STATUS[status])
    if ip is not None:
        order_by.append('ipmi_ip ' + ORDER_STATUS[ip])
    cluster = request.args.get('cluster', 2, type=int)
    search = request.args.get('content')
    search_type = request.args.get('search_type')
    search_form = SearchServiceForm()
    is_search = False
    if search_form.validate_on_submit() or search:
        if search and search_type:
            search_form.search_content.data = search
            search_form.search_type.data = search_type
        services = search_form.get_result(search, search_type, cluster)
        if services:
            services = services.order_by(*order_by).paginate(page, pageset, False)
        is_search = True

    if cluster == 2:
        versions = ServiceVersion.query.filter_by(type=1).all()
        machineform = AddMachineForm()
        if is_search:
            return render_template('auth/index.html', search_form=search_form, machineform=machineform,
                                   services=services,
                                   status=status, ip=ip, versions=versions, pageset=pageset, cluster=cluster)
        services = Service.query.filter_by(cluster_id=cluster).order_by(*order_by).paginate(page, pageset, False)
        return render_template('auth/index.html', machineform=machineform, search_form=search_form, services=services,
                               status=status, ip=ip, versions=versions, pageset=pageset, cluster=cluster)
    elif cluster == 1:
        versions = ServiceVersion.query.filter_by(type=2).all()
        machineform = AddMachineForm()
        if is_search:
            return render_template('auth/index.html', search_form=search_form, machineform=machineform,
                                   services=services,
                                   status=status, ip=ip, versions=versions, pageset=pageset, cluster=cluster)
        services = Service.query.filter_by(cluster_id=cluster).order_by(*order_by).paginate(page, pageset, False)
        return render_template('auth/index.html', machineform=machineform, search_form=search_form, services=services,
                               status=status, ip=ip, versions=versions, pageset=pageset, cluster=cluster)


@service.route('/machine_option', methods=['POST'])
@login_required
@check_ipxe_status
@csrf.exempt
def machine_option():
    if request.method == 'POST':
        machineform = AddMachineForm()
        if machineform.validate_on_submit():
            ipstarts, ipends = validate_ipaddress(machineform.startip.data, machineform.endip.data)
            if not ipstarts and not ipends:
                flash(u'请检查IP格式', 'danger')
                return redirect(url_for('service.index'))
            ssh_machine_shell(ipstarts, ends=ipends, option=machineform.option.data, option_ip=request.remote_addr)
            flash(u'操作成功请稍后刷新页面查看结果', 'success')
            return redirect(url_for('service.index'))
        return redirect(request.referrer)


@service.route('/single_service_option/<string:options>/<int:service_id>')
@login_required
@check_ipxe_status
def single_service_option(options, service_id):
    option_ip = request.remote_addr
    service = Service.query.filter_by(id=service_id).first()
    if service.status == 0 and options == "soft":
        flash(u"机器已经关机", "danger")
    if service.status == 2 and options == "reset":
        flash(u"已经在重启中", "danger")
    if service.status == 1 and options == 'on':
        flash(u"已经开机", "danger")
    else:
        ssh_machine_shell(service.ip, option=options, option_ip=option_ip)
        flash(u'操作成功', "success")
    return redirect(request.referrer)


@service.route('/service_upload/<int:service_id>', methods=["POST"])
@login_required
# @check_ipxe_status
def service_upload(service_id):
    import re
    cluster = request.args.get('cluster', 2, type=int)
    service = Service.query.filter_by(id=service_id).first_or_404()
    version = request.form.get("new_version")
    mach = re.match(VERSION_RE, version)
    if not mach:
        flash(u'版本号格式错误', 'danger')
    description = request.form.get("description")
    service_version = ServiceVersion.query.filter_by(version=version).first()
    cluster = service.cluster_id
    if service_version:
        flash(u'版本号已存在', 'danger')
        return redirect(request.referrer)
    if cluster == 2:
        if version and description:
            service_version = ServiceVersion(version, description)
            service_version = service_version.save()
            service = service_last_options(service, request.remote_addr)
            service.version_id = service_version.id
            service.status = 4
            service = service.save()
            ssh_machine_shell(service.ip, option='on', option_ip=request.remote_addr)
            flash(u'版本上传中，请稍后', 'success')
            return redirect(request.referrer)
        return redirect(request.referrer)
    elif cluster == 1:
        # try:
        from datetime import datetime
        description = "vh{version}_{ip}@{date}".format(version=service.version, ip=service.ip, date=datetime.strftime(datetime.now(), '%Y%m%d%H'))
        service = service_last_options(service, request.remote_addr)
        service_version = ServiceVersion(version, description, type=2)
        service_version = service_version.save()
        service.iscsi_status = 2
        service = service.save()
        start_disckless_backup(service, service_version)
        flash(u'备份母盘成功', 'success')
        return redirect(request.referrer)
        # except NotExisted as ne:
        #     current_app.logger.error(ne.description)
        #     flash('error:' + ne.description, 'danger')
        #     return redirect(request.referrer)
        # except Exception as e:
        #     current_app.logger.error(e.message)
        #     flash('error:' + e.message, 'danger')
        #     return redirect(request.referrer)


@service.route('/echo_machine_record')
def echolog():
    records = MachineRecord.query.order_by(MachineRecord.id.desc()).all()
    return render_template('auth/echo_log.html', records=records)


@service.route('/renew_services', methods=['POST'])
@login_required
#@check_ipxe_status
@csrf.exempt
def renew_services():
    # try:
    cluster = request.args.get('cluster', 2, type=int)
    version = request.form.get('version', type=int)
    option = request.form.get('option')
    ids = request.form.getlist('service_id', type=int)
    for service_id in ids:
        service = Service.query.filter_by(id=service_id).first_or_404()
        service = service_last_options(service, request.remote_addr)
        service.status = 2
        if option == 'now':
            flash(u'机器正在重装中，请注意日志', 'success')
            if cluster == 1:
                service.new_version_id = service
                service.version_id = version
                service.iscsi_status = 0
                shutdown_server(service.ip)
            else:
                service.version_id = version
                ssh_machine_shell(service.ip, option='reset', option_ip=request.remote_addr)
        else:
            flash(u'机器将在下次重启时重装，请注意查看日志', 'success')
        service = service.save()
        return redirect(request.referrer)
    # except NotExisted as ne:
    #     flash(u'重装失败', 'danger')
    #     save_machinerecord_log(service.ip, ne.description, request.remote_addr)
    #     current_app.logger.error('error in renew service')
    #     current_app.logger.error(ne.description)
    #     return redirect(request.referrer)
    # except Exception as e:
    #     flash(u'重装失败', 'danger')
    #     save_machinerecord_log(service.ip, e, request.remote_addr)
    #     current_app.logger.error('error in renew service')
    #     current_app.logger.error(e)
    #     return redirect(request.referrer)


@service.route("/check_start_status/aoe.ipxe")
@api_check_ipxe_status
def get_service_status():
    request_ip = request.remote_addr
    service = Service.query.filter_by(ip=request_ip).first()
    if not service:
        return json_response(1, error_msg='error')
    filename = 'aoe.ipxe'
    if service.status in [2, 4]:
        save_machinerecord_log(service.ip, u'机器引导中', request_ip)
        configs = current_app.config['DHCP_NETWORK_START']
    else:
        configs = current_app.config['BOOT_START']
        service.status = 1
        service.save()
    return response_file(data=configs, filename=filename)


@service.route("/service_config_file/install.bat")
@api_check_ipxe_status
def service_config_file():
    request_ip = request.remote_addr
    service = Service.query.filter_by(ip=request_ip).first()
    if not service:
        current_app.logger.error(request_ip + 'not in service')
        return json_response(1)
    filename = 'install.bat'
    configs = ''
    if service.status in [2, 3]:
        service.status = 3
        service.save()
        save_machinerecord_log(service.ip, u'开始重装系统', request_ip)
        configs = render_template('renew.bat', version=service.version)
        # configs = current_app.config['RENEW_SERVICE'].format(version=service.version)
    elif service.status in [4, 5]:
        service.status = 5
        service.save()
        save_machinerecord_log(service.ip, u'开始备份系统', request_ip)

        configs = render_template('upload.bat', version=service.version)
    return response_file(data=configs, filename=filename)


@service.route("/notification_service_status/")
@api_check_ipxe_status
def notification_service_status():
    request_ip = request.remote_addr
    service = Service.query.filter_by(ip=request_ip).first()
    if not service:
        current_app.logger.error(request_ip + 'not in service')
        return json_response(1)
    if service.status == 3:
        result = u'系统重装完成,准备开机'
    if service.status == 5:
        result = u'系统备份完成,准备开机'
    else:
        result = u'操作完成,准备开机'
    save_machinerecord_log(service.ip, result, option_ip=request_ip)
    service.status = 6
    service.save()
    return json_response(0)


@service.route("/service_start/")
@api_check_ipxe_status
def service_start():
    request_ip = request.remote_addr
    service = Service.query.filter_by(ip=request_ip).first()
    if not service:
        current_app.logger.error(request_ip + 'not in service')
        return json_response(1)
    service.status = 1
    service.save()
    return json_response(0)




@service.route("/start_disckless/")
def start_disckless():
    request_ip = request.remote_addr
    # try:
    save_machinerecord_log(request_ip, u'开始重装系统', request_ip)
    service = Service.query.filter_by(ip=request_ip).first()
    if service.iscsi_status == 0:
        start_disckless_reload(service, 'upgrade', service.new_version)
    elif service.iscsi_status == 1:
        version = ServiceVersion.query.filter_by(id=service.version_id).first()
        start_disckless_reload(service, 'reboot', version)
    return json_response(0)
    # except NotExisted as ne:
    #     current_app.logger.error(ne.description)
    #     save_machinerecord_log(request_ip, 'reload error:' + ne.description, request_ip)
    # except Exception as e:
    #     current_app.logger.error(e.message)
    #     save_machinerecord_log(request_ip, 'reload error:' + e.message, request_ip)
