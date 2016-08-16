# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash
from rgcpis.extensions import csrf
from flask_login import current_app, login_required, current_user
from flask_login import request
from rgcpis.service.logic import validate_ipaddress, ssh_machine_shell, renew_machine_options, upload_machine_options
from rgcpis.service.models import Service, MachineRecord, ServiceVersion
from rgcpis.utils.auth import json_response, response_file

service = Blueprint('service', __name__)
COPAY_PER_PAGE = 20


def stream_template(template_name, **context):
    current_app.update_template_context(context)
    t = current_app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv


order_status = {1: 'desc', 0: 'asc'}


@service.route('/')
@login_required
def index():
    user = current_user
    if current_user is None and not current_user.is_authenticated:
        return redirect(url_for("users.login"))

    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', type=int)
    ip = request.args.get('ip', type=int)
    versions = ServiceVersion.query.all()
    order_by = []
    if status is not None:
        order_by.append('status ' + order_status[status])
    if ip is not None:
        order_by.append('ipmi_ip ' + order_status[ip])
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


@service.route('/service_options/<int:service_id>', methods=["GET", "POST"])
def renew_service(service_id):
    service = Service.query.filter_by(id=service_id).first()
    renew_machine_options(service.ip)
    flash(u'机器正在重装中，请注意日志', 'success')
    return redirect(request.referrer)


@service.route('/service_upload/<int:service_id>', methods=["POST"])
def service_upload(service_id):
    version = request.form.get("new_version", type=float)
    option = request.form.get("option")
    if version:
        service = Service.query.filter_by(id=service_id).first_or_404()
        upload_machine_options(service, option)
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
    version = request.form.get('version')
    option = request.form.get('option')
    ids = request.form.getlist('service_id', type=int)
    for service_id in ids:
        service = Service.query.filter_by(id=service_id)
        if option == 'now':
            ssh_machine_shell(service.ip, option='restart')

    for id in ids:
        service = Service.query.filter_by(id=id).first()
        if service.status == 1:
            pass
        elif service.status == 0:
            pass
    flash(u'已开始', 'success')
    return redirect(request.referrer)


@service.route("/get_service_status")
def get_service_status():
    request_ip = request.remote_addr
    service = Service.query.filter_by(ip=request_ip).first()
    if not service:
        return json_response(1, error_msg='error')
    if service.status in [0, 1]:
        filename = ''
        configs = ''
    else:
        if service.status == 5:
            filename = ''
            configs = ''
        else:
            filename = ''
            configs = ''
    return response_file(data=configs, filename=filename)


@service.route("/service_config_file/")
def service_config_file():
    request_ip = request.remote_addr
    print request_ip
    service = Service.query.filter_by(ip=request_ip).first()
    # if not service:
    #     return json_response(1, error_msg='error')
    # if service.status in [0, 1]:
    filename = 'aoe_b.ipxe'
    configs = '#!ipxe\nsanboot --no-describe --drive 0x80'
    # else:
    #     if service.status == 5:
    # filename = 'aoe_a.ipxe'
    # configs = "#!ipxe\nset keep-san 1\nchain http://172.20.0.51/winpe/winpe/wimboot_a.ipxe"
    #     else:
    #         filename = ''
    #         configs = ''
    return response_file(data=configs, filename=filename)
