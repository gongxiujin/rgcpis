# -*- coding: utf-8 -*-
import MySQLdb
import os

# VER_A = '2.0.4'
# VER_B = '1.2.2'
# VER_C = 'linux'
# VER_D = 'bakup'
#
# os.unlink("dhcpd.conf")
# f = open('dhcp_tou.txt')
#
dhcpfile = open('dhcpd.conf', 'w')
# content = f.read()
# dhcpfile.write(content)
# f.close()

IPXE_A = """if exists user-class and option user-class = "iPXE" {
        filename "http://172.20.0.51/winpe/aoe_a.ipxe";
    } else {
         filename "undionly.kpxe";
    }\n"""
IPXE_B = """if exists user-class and option user-class = "iPXE" {
        filename "http://172.20.0.51/winpe/aoe_b.ipxe";
    } else {
         filename "undionly.kpxe";
    }\n"""
IPXE_C = """if exists user-class and option user-class = "iPXE" {
        filename "http://172.20.0.51/winpe/aoe_c.ipxe";
    } else {
         filename "undionly.kpxe";
    }\n"""
IPXE_D = """if exists user-class and option user-class = "iPXE" {
        filename "http://172.20.0.51/winpe/aoe_d.ipxe";
    } else {
         filename "undionly.kpxe";
    }\n"""
IPXE_STATUS = {0:IPXE_A, 1:IPXE_B}

def options_service(version, services):
    try:

        for service in services:
            AA1 = """######################################### {ip}
            host {ip} {
            hardware ethernet {mac};
            option host-name "{ip}";
            option domain-name "renderg.com";
            fixed-address {ip};
            option routers 172.20.0.1;
            }""".format(ip=service.ip, mac=service.mac)
            dhcpfile.write(AA1)
            # AA2 = 'host' + ' ' + ip + '{\n'
            # dhcpfile.write(AA2)
            # AA3 = 'hardware ethernet ' + mac + ';\n'
            # dhcpfile.write(AA3)
            # AA4 = 'option host-name "' + ip + '";\n'
            # dhcpfile.write(AA4)
            # AA5 = 'option domain-name "renderg.com";\n'
            # dhcpfile.write(AA5)
            # AA6 = 'fixed-address ' + ip + ';\n'
            # dhcpfile.write(AA6)
            # AA7 = 'option routers 172.20.0.1;\n'
            # dhcpfile.write(AA7)
            if service.status == 1:
                pass
                # if version == VER_A:
                #     dhcpfile.write(IPXE_A)
                # if version == VER_B:
                #     dhcpfile.write(IPXE_B)
                # if version == VER_C:
                #     dhcpfile.write(IPXE_C)
                # if version == VER_D:
                #     dhcpfile.write(IPXE_D)
            dhcpfile.write("}\n")
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
dhcpfile.write("}\n")
dhcpfile.close()
os.system('systemctl restart dhcpd')
os.system('systemctl status dhcpd')
