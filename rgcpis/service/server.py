# coding=utf8
import os, sys
from threading import Thread
from rpyc import Service
from rpyc.utils.server import ThreadedServer
import time
import subprocess


class Shutdown(Thread):
    def stop(self):
        self.thread_stop = True

    def run(self):
        time.sleep(5)
        subprocess.Popen('shutdown -f -r -t 5', shell=True)


class StockService(Service):
    def __init__(self, conn):
        super(StockService, self).__init__(conn)

    def exposed_get_time(self):
        return time.ctime()

    def exposed_shutdown(self):
        try:
            t = Shutdown()
            t.start()
            # res = subprocess.Popen('shutdown -f -r -t 3', shell=True)
            # result = pexpect.spawn('shutdown -f -r -t 3')
            return {'status': True}
        except Exception as e:
            return {'status': False, 'result': 'error'}

            # result = pexpect.spawn('shutdown -f -r -t 3')
            # if not result.read():
            #     return {'status': True}
            # else:
            #     return {'status':False, 'result':result.read()}


if __name__ == '__main__':
    s = ThreadedServer(StockService, port=60000, auto_register=False)
    s.start()
