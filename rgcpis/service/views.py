# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_app
from flask_login import request
from rgcpis.service.logic import validate_ipaddress, ssh_machine_shell
from rgcpis.service.models import Service, MachineRecord

service = Blueprint('service', __name__)
COPAY_PER_PAGE = 20


def stream_template(template_name, **context):
    current_app.update_template_context(context)
    t = current_app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv


order_status = {1: 'desc', 0: 'asc'}


@service.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', type=int)
    ip = request.args.get('ip', type=int)
    order_by = []
    if status is not None:
        order_by.append('status ' + order_status[status])
    if ip is not None:
        order_by.append('ipmi_ip ' + order_status[ip])
    services = Service.query.order_by(*order_by).paginate(page, COPAY_PER_PAGE, False)
    return render_template('auth/index.html', services=services, status=status, ip=ip)


@service.route('/add_machine', methods=['POST'])
def add_machine():
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


@service.route('echo_machine_record')
def echolog():
    records = MachineRecord.query.order_by(MachineRecord.id.desc()).all()
    return render_template('auth/echo_log.html', records=records)
