#!/usr/bin/env python
# vim: expandtab sw=4 ts=4:
#
# retrieve the number of OSPF routes on Palto Alto firewalls throught CLI by SSH
#
# 2018-10-29 Eric Belhomme <eric.belhomme@axians.com> - Initial write

import argparse, paramiko, re
from pprint import pprint

def getPaltoAltoRoutes(fwServer, fwUser, fwPasswd):
    # dFlags = {
    #     'A': 'active',
    #     '?': 'loose',
    #     'C': 'connect',
    #     'H': 'host',
    #     'S': 'static',
    #     '~': 'internal',
    #     'R': 'rip',
    #     'O': 'ospf',
    #     'B': 'bgp',
    #     'Oi': 'ospf intra-area',
    #     'Oo': 'ospf inter-area',
    #     'O1': 'ospf ext-type-1',
    #     'O2': 'ospf ext-type-2',
    #     'E': 'ecmp',
    #     'M': 'multicast',
    # }
    
    routes = []
    reroute = re.compile('^(?P<dest>[\d{1,3}\./]+)\s+(?P<hop>[\d{1,3}\.]+)\s+(?P<metric>\d+)\s+(?P<flags>[\?ACHS~ROBio12EM ]+)\s(?P<age>\d+)\s(?P<interface>[\w\d\.]+)\s*$')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect( fwServer, username=fwUser, password=fwPasswd)
    stdin, stdout, stderr = ssh.exec_command("")
    
    stdin.write("show routing route type ospf\n")
    stdin.flush()
    
    line = stdout.next()
    while line:
        match = reroute.match(line)
        if match:
            routes.append(
                {
                    'destination': match.group('dest'),
                    'gateway': match.group('hop'),
                    'metric': match.group('metric'),
                    'flags': match.group('flags').strip().rstrip().split(' '),
                    'age':  match.group('age'),
                    'interface': match.group('interface'),
                }
            )
        if line.startswith('total'):
            break
        line = stdout.next()
    ssh.close()
    return routes


def getFortinetRoutes(fwServer, fwUser, fwPasswd):
    routes = []
    reroute = re.compile('^O(\*|\s)(?P<flags>N1|E1|E2)?\s+(?P<dest>[\d{1,3}\.\/]+)\s+.*via\s(?P<hop>[0-9\.]+),\s+(?P<interface>.+),\s+((?P<agew>\d+)w)?((?P<aged>\d+)d)?((?P<ageh>\d+)h)?((?P<agem>\d+)m)?\s*$')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect( fwServer, username=fwUser, password=fwPasswd)
    stdin, stdout, stderr = ssh.exec_command("get router info routing-table ospf")
    
#    stdin.write("get router info routing-table ospf\n")
#    stdin.flush()
    
    line = stdout.next()
    while line:
        match = reroute.match(line)
        if match:
            age = 0
            if match.group('agew') > 0:
                age += int(match.group('agew')) * 7 * 86400
            if match.group('aged') > 0:
                age += int(match.group('aged')) * 86400
            if match.group('ageh') > 0:
                age += int(match.group('ageh')) * 3600
            if match.group('agem') > 0:
                age += int(match.group('agem')) * 60

            if match.group('flags') > 0:
                flags = match.group('flags').strip().rstrip().split(' ')
            else:
                flags =[]
            routes.append(
                {
                    'destination': match.group('dest'),
                    'gateway': match.group('hop'),
                    'metric': '0',
                    'flags': flags,
                    'age': str(age),
                    'interface': match.group('interface'),
                }
            )
        if line.endswith('$'):
            break
        try:
            line = stdout.next()
        except StopIteration:
            break;        

    ssh.close()
    return routes


parser = argparse.ArgumentParser(description='Nagios check for OSPF routes count, for Fortinet and PaloAlto firewalls')
parser.add_argument('-H', '--hostname', type=str, help='hostname or IP address', required=True)
parser.add_argument('-U', '--username', type=str, help='username', required=True)
parser.add_argument('-P', '--password', type=str, help='user password', required=True)
parser.add_argument('-t', '--type', type=str, help='FW type (Palo, Forti)', choices=['paloalto', 'fortinet'], required=True)
parser.add_argument('-p', '--perfdata', help='enable pnp4nagios perfdata', action='store_true')
parser.add_argument('-w', '--warning', type=int, nargs='?', help='warning trigger', default=10)
parser.add_argument('-c', '--critical', type=int, nargs='?', help='critical trigger', default=6)

args = parser.parse_args()


retcode = 0
message = "OK: "

routes = []
if args.type.startswith('paloalto'):
    routes = getPaltoAltoRoutes(args.hostname, args.username, args.password)
elif args.type.startswith('fortinet'):
    routes = getFortinetRoutes(args.hostname, args.username, args.password)

if len(routes) <= args.warning:
    retcode = 1
    message = "WARNING: "
if len(routes) <= args.critical:
    retcode = 2
    message = "CRITICAL: "

if len(routes) == 0:
    message += "{} no active routes found.\n"
else:
    message += "{} active routes found :\n".format(len(routes))
    for route in routes:
        message += "dest. {} via {}\n".format(route['destination'], route['gateway'])

if args.perfdata:
    message += "| routes={};{};{}".format(len(routes), args.warning, args.critical)

print(message)
exit(retcode)
