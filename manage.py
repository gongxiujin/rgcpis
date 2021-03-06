from flask_script import Manager, Server, Shell, prompt, prompt_pass
from rgcpis.app import create_app
from rgcpis.extensions import db
import time
from flask_login import current_app
from flask_migrate import MigrateCommand
from rgcpis.service.logic import ssh_query_activity_machine
from rgcpis.service.models import Service
from rgcpis.config.default import DefaultConfig as config
from rgcpis.user.logic import create_admin_user

app = create_app(config)
manager = Manager(app)
SSH_QUEUE_ID = 'query_activity_machine'
manager.add_command("runserver", Server("localhost", port=8080))

manager.add_command('db', MigrateCommand)


def make_shell_context():
    return dict(app=current_app, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def start_query_machine_queue():
    # from apscheduler.schedulers.blocking import BlockingScheduler
    # sched = BlockingScheduler()
    # sched.add_job(ssh_query_activity_machine, 'cron', minute=3, id=SSH_QUEUE_ID)
    # sched.start()
    while True:
        ssh_query_activity_machine()
        time.sleep(300)


# @manager.command
# def shutdown_query_machine_queue():
#     from apscheduler.schedulers.blocking import BlockingScheduler
#     sched = BlockingScheduler()
#     runsche = sched.get_job(SSH_QUEUE_ID)
#     runsche.pause()


@manager.option('-offset')
def init_service_machines(offset):
    with app.app_context():
        current_app.logger.info('strt')
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
                    new_service.set_ipmiip(offset)
                    new_service.save()
    print 'over'

@manager.command
def init_disckless_machines():
    with app.app_context():
        current_app.logger.info('strt')
        ips = ['172.17.2.{}'.format(i) for i in xrange(1, 151)]+['172.17.3.{}'.format(x) for x in xrange(1, 254)]
        services = {}
        for i in ips:
            split_ip = i.split('.')
            services[i] = '192.168.{:03d}.{:03d}'.format(int(split_ip[-2]), int(split_ip[-1]))
        for ip in services:
            new_service = Service(ip, iscsi_status=1, cluster_id=1)
            new_service.ipmi_ip = services[ip]
            new_service.save()

    print 'over'

@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
def create_admin(username=None, password=None, email=None):
    """Creates the admin user."""

    if not (username and password and email):
        username = prompt("Username")
        password = prompt_pass("Password")

    create_admin_user(username=username, password=password)


if __name__ == '__main__':
    manager.run()
