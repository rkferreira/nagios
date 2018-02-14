#!/usr/bin/python

'''
* DESCRIPTION :
*       EMC Unity Storage monitoring
*
* AUTHOR :    Rodrigo Ferreira <rkferreira@gmail.com>   START DATE :    07 Feb 2018
*
* CHANGES :
*
* VERSION	DATE		WHO						DETAIL
* 0.1		07Feb18		Rodrigo Ferreira <rkferreira@gmail.com>		Initial version
*
'''

import json, requests
import argparse
import sys


'''
## Nagios
#
0	OK		The plugin was able to check the service and it appeared to be functioning properly
1	Warning		The plugin was able to check the service, but it appeared to be above some "warning" threshold or did not appear to be working properly
2	Critical	The plugin detected that either the service was not running or it was above some "critical" threshold
3	Unknown		Invalid command line arguments were supplied to the plugin or low-level failures internal to the plugin (such as unable to fork, or open a tcp socket) that prevent it from performing 
			the specified operation. Higher-level errors (such as name resolution errors, socket timeouts, etc) are outside of the control of plugins and should generally NOT be reported as 
			UNKNOWN states.

## health (EMC Unity)
#
value		HealthEnum	Health value.
descriptionIds	List<String>	Description ids.
descriptions	List<String>	Descriptions are localized messages describing details of the operating condition.
resolutionIds	List<String>	Resolution ids.
resolutions	List<String>	Resolutions are URLs to get more information about this health state.

## HealthEnum (EMC Unity)
#
0		UNKNOWN		Unknown.
5		OK		OK.
7		OK_BUT		OK But Minor Warning.
10		DEGRADED	Degraded.
15		MINOR		Minor Issue.
20		MAJOR		Major Issue.
25		CRITICAL	Critical Issue.
30		NON_RECOVERABLE	Non Recoverable Issue. 

'''
def NagiosStatus(value, descid, desc):
	if value == 0:
		return ('UNKNOWN', descid, desc, value)
	else:
		if value == 5:
			return ('OK', descid, desc, value)
		else:
			if (value > 5 and value < 20):
				return ('WARNING', descid, desc, value)
			else:
				if value >= 20:
					return ('CRITICAL', descid, desc, value)
	return False


def EmptyOK():
	return (5, 'GOT_EMPTY_FROM_UNITY', 'I got no entries in the entries list of HEALTH.')


## Information about general settings for the storage system. 
#
def getSystem(hostaddress, token, cookie):
	baseurl = '/api/types/system/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options
	
	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	descid = str(j['entries'][0]['content']['health']['descriptionIds'][0])
	desc   = str(j['entries'][0]['content']['health']['descriptions'][0])
	value  = j['entries'][0]['content']['health']['value']

	return (value, descid, desc)


## (Applies to physical deployments only.) Information about batteries in the storage system. 
#
def getBattery(hostaddress, token, cookie):
	baseurl = '/api/types/battery/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	for x in j['entries']:
		#print x
		descid = str(x['content']['health']['descriptionIds'][0])
		desc   = str(x['content']['health']['descriptions'][0])
		value  = x['content']['health']['value']
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		if (s_nagios != "OK"):
			return (value, descid, desc)

	return (value, descid, desc)


## Information about Disk Array Enclosure (DAE) components in the storage system. 
#
def getDae(hostaddress, token, cookie):
	baseurl = '/api/types/dae/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	for x in j['entries']:
		#print x
		descid = str(x['content']['health']['descriptionIds'][0])
		desc   = str(x['content']['health']['descriptions'][0])
		value  = x['content']['health']['value']
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		if (s_nagios != "OK"):
			return (value, descid, desc)

	return (value, descid, desc)


## Information about the disks's attributes in the storage system. 
#
def getDisk(hostaddress, token, cookie):
	baseurl = '/api/types/disk/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options
	
	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	for x in j['entries']:
		#print x
		descid = str(x['content']['health']['descriptionIds'][0])
		desc   = str(x['content']['health']['descriptions'][0])
		value  = x['content']['health']['value']
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		if (s_nagios != "OK"):
			return (value, descid, desc)

	return (value, descid, desc)


## Information about Disk Processor Enclosures (DPEs) in the storage system. 
#
def getDpe(hostaddress, token, cookie):
	baseurl = '/api/types/dpe/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	descid = str(j['entries'][0]['content']['health']['descriptionIds'][0])
	desc   = str(j['entries'][0]['content']['health']['descriptions'][0])
	value  = j['entries'][0]['content']['health']['value']

	return (value, descid, desc)


## Information about Ethernet ports in the storage system. 
#
def getEthernetport(hostaddress, token, cookie):
	baseurl = '/api/types/ethernetPort/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	for x in j['entries']:
		#print x
		descid = str(x['content']['health']['descriptionIds'][0])
		desc   = str(x['content']['health']['descriptions'][0])
		value  = x['content']['health']['value']
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		if (s_nagios != "OK"):
			return (value, descid, desc)

	return (value, descid, desc)


## (Applies to physical deployments only.) Information about the fans in the storage system.
#
def getFan(hostaddress, token, cookie):
	baseurl = '/api/types/fan/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	for x in j['entries']:
		#print x
		descid = str(x['content']['health']['descriptionIds'][0])
		desc   = str(x['content']['health']['descriptions'][0])
		value  = x['content']['health']['value']
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		if (s_nagios != "OK"):
			return (value, descid, desc)

	return (value, descid, desc)


## Fibre Channel (FC) front end port settings. Applies if the FC protocol is supported on the system and the corresponding license is installed.
#
def getFcport(hostaddress, token, cookie):
	baseurl = '/api/types/fcPort/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	for x in j['entries']:
		#print x
		descid = str(x['content']['health']['descriptionIds'][0])
		desc   = str(x['content']['health']['descriptions'][0])
		value  = x['content']['health']['value']
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		if (s_nagios != "OK"):
			return (value, descid, desc)

	return (value, descid, desc)


## (Applies to physical deployments only.) Information about I/O module SLICs (small I/O cards) in the storage system. I/O modules provide connectivity between SPs and Disk-Array Enclosures (DAEs). 
#
def getIomodule(hostaddress, token, cookie):
	baseurl = '/api/types/ioModule/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	for x in j['entries']:
		#print x
		descid = str(x['content']['health']['descriptionIds'][0])
		desc   = str(x['content']['health']['descriptions'][0])
		value  = x['content']['health']['value']
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		if (s_nagios != "OK"):
			return (value, descid, desc)

	return (value, descid, desc)


## (Applies to physical deployments only.) Information about Link Control Cards (LCCs) in the storage system. 
#
def getLcc(hostaddress, token, cookie):
	baseurl = '/api/types/lcc/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	for x in j['entries']:
		#print x
		descid = str(x['content']['health']['descriptionIds'][0])
		desc   = str(x['content']['health']['descriptions'][0])
		value  = x['content']['health']['value']
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		if (s_nagios != "OK"):
			return (value, descid, desc)

	return (value, descid, desc)


## (Applies to physical deployments only.) Information about memory modules in the storage system.
#
def getMemorymodule(hostaddress, token, cookie):
	baseurl = '/api/types/memoryModule/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	for x in j['entries']:
		#print x
		descid = str(x['content']['health']['descriptionIds'][0])
		desc   = str(x['content']['health']['descriptions'][0])
		value  = x['content']['health']['value']
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		if (s_nagios != "OK"):
			return (value, descid, desc)

	return (value, descid, desc)


## (Applies to physical deployments only.) Information about power supplies in the storage system.
#
def getPowersupply(hostaddress, token, cookie):
	baseurl = '/api/types/powerSupply/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	for x in j['entries']:
		#print x
		descid = str(x['content']['health']['descriptionIds'][0])
		desc   = str(x['content']['health']['descriptions'][0])
		value  = x['content']['health']['value']
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		if (s_nagios != "OK"):
			return (value, descid, desc)

	return (value, descid, desc)


## (Applies to physical deployments only.) Information about Serial Attached SCSI (SAS) ports in the storage system. 
#
def getSasport(hostaddress, token, cookie):
	baseurl = '/api/types/sasPort/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	for x in j['entries']:
		#print x
		descid = str(x['content']['health']['descriptionIds'][0])
		desc   = str(x['content']['health']['descriptions'][0])
		value  = x['content']['health']['value']
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		if (s_nagios != "OK"):
			return (value, descid, desc)

	return (value, descid, desc)


## (Applies to physical deployments only.) Information about System Status Cards (SSCs) in the storage system. 
#
def getSsc(hostaddress, token, cookie):
	baseurl = '/api/types/ssc/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)

	if not j['entries']:
		value, descid, desc = EmptyOK()
	else:
		for x in j['entries']:
			#print x
			descid = str(x['content']['health']['descriptionIds'][0])
			desc   = str(x['content']['health']['descriptions'][0])
			value  = x['content']['health']['value']
			s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
			if (s_nagios != "OK"):
				return (value, descid, desc)

	return (value, descid, desc)


## (Applies to physical deployments only.) Information about internal Flash-based Solid State Disks (SSDs, mSATAs) in the storage system. 
#
def getSsd(hostaddress, token, cookie):
	baseurl = '/api/types/ssd/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)
	
	for x in j['entries']:
		#print x
		descid = str(x['content']['health']['descriptionIds'][0])
		desc   = str(x['content']['health']['descriptions'][0])
		value  = x['content']['health']['value']
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		if (s_nagios != "OK"):
			return (value, descid, desc)

	return (value, descid, desc)


## Information about Storage Processors (SPs) in the storage system.
#
def getStorageprocessor(hostaddress, token, cookie):
	baseurl = '/api/types/storageProcessor/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)
	
	for x in j['entries']:
		#print x
		descid = str(x['content']['health']['descriptionIds'][0])
		desc   = str(x['content']['health']['descriptions'][0])
		value  = x['content']['health']['value']
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		if (s_nagios != "OK"):
			return (value, descid, desc)

	return (value, descid, desc)


## (Applies to physical deployments only.) Information about Uncommitted ports in the storage system.
#
def getUncommittedport(hostaddress, token, cookie):
	baseurl = '/api/types/uncommittedPort/instances'
	options = '?fields=health,id&per_page=2000&compact=true'
	requrl  = 'https://'+hostaddress+baseurl+options

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'EMC-CSRF-TOKEN': token}
	r = requests.get(requrl, headers=headers, verify=False, cookies=cookie)
	j = json.loads(r.text)
	
	if not j['entries']:
		value, descid, desc = EmptyOK()
	else:
		for x in j['entries']:
			#print x
			descid = str(x['content']['health']['descriptionIds'][0])
			desc   = str(x['content']['health']['descriptions'][0])
			value  = x['content']['health']['value']
			s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
			if (s_nagios != "OK"):
				return (value, descid, desc)

	return (value, descid, desc)


def login(hostaddress, user, password):
	baseurl = '/api/types/loginSessionInfo'
	requrl  = 'https://'+hostaddress+baseurl

	headers = {'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
	r = requests.get(requrl, headers=headers, verify=False, auth=(user, password))

	if r.status_code == 200:
		token  = r.headers['emc-csrf-token']
		cookie = r.cookies
	else:
		token  = 0
		cookie = 0

	return (token, cookie)


def main():
	parser = argparse.ArgumentParser(description="Script for EMC Unity Storage monitoring",epilog='''Example:  ./check_unity2.py -H 10.0.0.1 -m DAE -u user -p pass''')
	parser.add_argument("-H", "--hostaddress", type=str, required=True, help="Host address for the URL")
	parser.add_argument("-u", "--user", type=str, required=True, help="Username for system login")
	parser.add_argument("-p", "--password", type=str, required=True, help="Password for system login")
	parser.add_argument("-m", "--module", type=str, choices=['battery','dae','disk','dpe','ethernetport','fan','fcport','iomodule','lcc','memorymodule','powersupply','sasport','ssc','ssd','storageprocessor','system','uncommittedport'], required=True, help="Requested MODULE for getting status. Possible options are: battery dae disk dpe ethernetport fan fcPort ioModule lcc memoryModule powerSupply sasPort ssc ssd storageProcessor system uncommittedPort")
	args = parser.parse_args()

	hostaddress	= args.hostaddress
	user		= args.user
	password	= args.password
	module		= args.module

	if (not hostaddress and not user and not password and not module):
		parser.print_help()
		sys.exit(1)

	token, cookie = login(hostaddress, user, password)

	value  = None
	descid = None
	desc   = None

	if (module.lower() == 'system'):
		value, descid, desc = getSystem(hostaddress, token, cookie)
	if (module.lower() == 'battery'):
		value, descid, desc = getBattery(hostaddress, token, cookie)
	if (module.lower() == 'dae'):
		value, descid, desc = getDae(hostaddress, token, cookie)
	if (module.lower() == 'disk'):
		value, descid, desc = getDisk(hostaddress, token, cookie)
	if (module.lower() == 'dpe'):
		value, descid, desc = getDpe(hostaddress, token, cookie)
	if (module.lower() == 'ethernetport'):
		value, descid, desc = getEthernetport(hostaddress, token, cookie)
	if (module.lower() == 'fan'):
		value, descid, desc = getFan(hostaddress, token, cookie)
	if (module.lower() == 'fcport'):
		value, descid, desc = getFcport(hostaddress, token, cookie)
	if (module.lower() == 'iomodule'):
		value, descid, desc = getIomodule(hostaddress, token, cookie)
	if (module.lower() == 'lcc'):
		value, descid, desc = getLcc(hostaddress, token, cookie)
	if (module.lower() == 'memorymodule'):
		value, descid, desc = getMemorymodule(hostaddress, token, cookie)
	if (module.lower() == 'powersupply'):
		value, descid, desc = getPowersupply(hostaddress, token, cookie)
	if (module.lower() == 'sasport'):
		value, descid, desc = getSasport(hostaddress, token, cookie)
	if (module.lower() == 'ssc'):
		value, descid, desc = getSsc(hostaddress, token, cookie)
	if (module.lower() == 'ssd'):
		value, descid, desc = getSsd(hostaddress, token, cookie)
	if (module.lower() == 'storageprocessor'):
		value, descid, desc = getStorageprocessor(hostaddress, token, cookie)
	if (module.lower() == 'uncommittedport'):
		value, descid, desc = getUncommittedport(hostaddress, token, cookie)
	
	if value and descid and desc:
		s_nagios, s_msg1, s_msg2, s_val = NagiosStatus(value, descid, desc)
		print ('%s: %s,%s,%s' % (s_nagios,s_msg1,s_msg2,s_val))
	sys.exit(0)


if __name__ == '__main__':
	main()
