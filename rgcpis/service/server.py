# coding=utf8
import os, sys
import pexpect
from rpyc import Service
from rpyc.utils.server import ThreadedServer
import time

class StockService(Service):
    def __init__(self, conn):
        super(StockService, self).__init__(conn)

    def exposed_get_time(self):
        return time.ctime()

    def exposed_shutdown(self):
        result = pexpect.spawn('shutdown /s now')
        if not result.read():
            return {'status': True}
        else:
            return {'status':False, 'result':result.read()}

if __name__ == '__main__':
    s = ThreadedServer(StockService, port=60000, auto_register=False)
    s.start()