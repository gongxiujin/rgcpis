from flask_script import Manager, Server, Shell
from rgcpis.app import create_app
from rgcpis.extensions import db
import time
from flask_login import current_app
from flask_migrate import MigrateCommand
from rgcpis.service.logic import ssh_query_activity_machine
from rgcpis.service.models import Service
from rgcpis.config.default import DefaultConfig as config

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


@manager.command
def shutdown_query_machine_queue():
    from apscheduler.schedulers.blocking import BlockingScheduler
    sched = BlockingScheduler()
    runsche = sched.get_job(SSH_QUEUE_ID)
    runsche.pause()


@manager.option('-offset')
def init_service_machines(offset):
    with app.app_context():
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
                    new_service.set_ipmiip(offset)
                    new_service.save()
    print 'over'


if __name__ == '__main__':
    manager.run()
