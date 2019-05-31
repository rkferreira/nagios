#!/usr/bin/python
# vim: set sw=3 ts=3 expandtab:

'''
* DESCRIPTION :
*       EMC Unity Storage monitoring
*
* AUTHOR :    Rodrigo Ferreira <rkferreira@gmail.com>   START DATE :    07 Feb 2018
              Eric Belhomme <eric.belhomme@free.fr>     START DATE :    05 Apr 2018
*
* CHANGES :
*
* VERSION   DATE     WHO                  DETAIL
* 0.1    07Feb18     Rodrigo Ferreira <rkferreira@gmail.com>      Initial version
* 0.2    15Feb18     Rodrigo Ferreira <rkferreira@gmail.com>      Minor fixes
* 0.3    22Feb18     Rodrigo Ferreira <rkferreira@gmail.com>      Fixed exit values
* 0.4    04Apr18     Eric Belhomme <eric.belhomme@free.fr>        code factorization and added http session code
*
'''

import json, requests
import argparse
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

'''
## Nagios
#
0  OK    The plugin was able to check the service and it appeared to be functioning properly
1  Warning     The plugin was able to check the service, but it appeared to be above some "warning" threshold or did not appear to be working properly
2  Critical The plugin detected that either the service was not running or it was above some "critical" threshold
3  Unknown     Invalid command line arguments were supplied to the plugin or low-level failures internal to the plugin (such as unable to fork, or open a tcp socket) that prevent it from performing 
         the specified operation. Higher-level errors (such as name resolution errors, socket timeouts, etc) are outside of the control of plugins and should generally NOT be reported as 
         UNKNOWN states.

## health (EMC Unity)
#
value    HealthEnum  Health value.
descriptionIds List<String>   Description ids.
descriptions   List<String>   Descriptions are localized messages describing details of the operating condition.
resolutionIds  List<String>   Resolution ids.
resolutions List<String>   Resolutions are URLs to get more information about this health state.

## HealthEnum (EMC Unity)
#
0     UNKNOWN     Unknown.
5     OK    OK.
7     OK_BUT      OK But Minor Warning.
10    DEGRADED Degraded.
15    MINOR    Minor Issue.
20    MAJOR    Major Issue.
25    CRITICAL Critical Issue.
30    NON_RECOVERABLE   Non Recoverable Issue. 

'''
def NagiosStatus(value, descid, desc):
   if value == 0:
      return ('UNKNOWN', descid, desc, value, 3)
   else:
      if value == 5:
         return ('OK', descid, desc, value, 0)
      else:
         if (value > 5 and value < 20):
            return ('WARNING', descid, desc, value, 1)
         else:
            if value >= 20:
               return ('CRITICAL', descid, desc, value, 2)
   return False


def EmptyOK():
   return (5, 'GOT_EMPTY_FROM_UNITY', 'I got no entries in the entries list of HEALTH.')

def EmptyCouldNotGet():
   return (0, 'COULD_NOT_REQUEST_URL', 'I could not request the API url')


## Information about general settings for the storage system. 
#
def getSystem(hostaddress, s):
   baseurl = '/api/types/system/instances'
   options = '?fields=health,id&per_page=2000&compact=true'
   requrl  = 'https://'+hostaddress+baseurl+options
   
   ret = 0
   sta = 0
   while ((sta != 200) or (ret < 4)):
      r = s.get(requrl)
      sta = r.status_code
      ret += 1
   try:
      j = json.loads(r.text)
      descid = str(j['entries'][0]['content']['health']['descriptionIds'][0])
      desc   = str(j['entries'][0]['content']['health']['descriptions'][0])
      value  = j['entries'][0]['content']['health']['value']
   except ValueError:
      value, descid, desc = EmptyCouldNotGet()

   return (value, descid, desc)


## A generic function to get health status of enclosure's components.
#
def httpGet(hostaddress, s, check):
   requrl  = 'https://'+hostaddress+'/api/types/'+check+'/instances?fields=health,id&per_page=2000&compact=true'
   r = s.get(requrl)
   j = json.loads(r.text)

   if not j['entries']:
      value, descid, desc = EmptyOK()
   else:
      for x in j['entries']:
         #print x
         descid = str(x['content']['health']['descriptionIds'][0])
         desc   = str(x['content']['health']['descriptions'][0])
         value  = x['content']['health']['value']
         s_nagios, s_msg1, s_msg2, s_val, s_exit = NagiosStatus(value, descid, desc)
         if (s_nagios != "OK"):
            return (value, descid, desc)

   return (value, descid, desc)


def main():
   parser = argparse.ArgumentParser(description="Script for EMC Unity Storage monitoring",epilog='''Example:  ./check_unity2.py -H 10.0.0.1 -m DAE -u user -p pass''')
   parser.add_argument("-H", "--hostaddress", type=str, required=True, help="Host address for the URL")
   parser.add_argument("-u", "--user", type=str, required=True, help="Username for system login")
   parser.add_argument("-p", "--password", type=str, required=True, help="Password for system login")
   parser.add_argument("-m", "--module", type=str, choices=['battery','dae','disk','dpe','ethernetport','fan','fcport','iomodule','lcc','memorymodule','powersupply','sasport','ssc','ssd','storageprocessor','system','uncommittedport'], required=True, help="Requested MODULE for getting status. Possible options are: battery dae disk dpe ethernetport fan fcPort ioModule lcc memoryModule powerSupply sasPort ssc ssd storageProcessor system uncommittedPort")
   args = parser.parse_args()

   hostaddress = args.hostaddress
   user     = args.user
   password = args.password
   module   = args.module

   if (not hostaddress and not user and not password and not module):
      parser.print_help()
      sys.exit(1)

   s = requests.Session()
   s.auth = (user, password)
   s.headers.update({'Accept': 'application/json', 'Content-type': 'application/json', 'X-EMC-REST-CLIENT': 'true'})
   s.verify = False

   value  = None
   descid = None
   desc   = None

   r = s.get('https://' + hostaddress + '/api/types/loginSessionInfo')
   if r.status_code == 200:
      s.headers.update({'EMC-CSRF-TOKEN': r.headers['EMC-CSRF-TOKEN']})

      # Information about general settings for the storage system.
      if (module.lower() == 'system'):
         value, descid, desc = getSystem(hostaddress, s)
      # (Applies to physical deployments only.) Information about batteries in the storage system.
      if (module.lower() == 'battery'):
         value, descid, desc = httpGet(hostaddress, s, 'battery')
      # Information about Disk Array Enclosure (DAE) components in the storage system. 
      if (module.lower() == 'dae'):
         value, descid, desc = httpGet(hostaddress, s, 'dae')
      # Information about the disks's attributes in the storage system. 
      if (module.lower() == 'disk'):
         value, descid, desc = httpGet(hostaddress, s, 'disk')
      # Information about Disk Processor Enclosures (DPEs) in the storage system. 
      if (module.lower() == 'dpe'):
         value, descid, desc = httpGet(hostaddress, s, 'dpe')
      # Information about Ethernet ports in the storage system. 
      if (module.lower() == 'ethernetport'):
         value, descid, desc = httpGet(hostaddress, s, 'ethernetPort')
      # (Applies to physical deployments only.) Information about the fans in the storage system.
      if (module.lower() == 'fan'):
         value, descid, desc = httpGet(hostaddress, s, 'fan')
      # Fibre Channel (FC) front end port settings. Applies if the FC protocol is supported
      # on the system and the corresponding license is installed.
      if (module.lower() == 'fcport'):
         value, descid, desc = httpGet(hostaddress, s, 'fcPort')
      # (Applies to physical deployments only.) Information about I/O module SLICs
      # (small I/O cards) in the storage system. I/O modules provide connectivity between
      # SPs and Disk-Array Enclosures (DAEs). 
      if (module.lower() == 'iomodule'):
         value, descid, desc = httpGet(hostaddress, s, 'ioModule')
      # (Applies to physical deployments only.) Information about Link Control
      # Cards (LCCs) in the storage system. 
      if (module.lower() == 'lcc'):
         value, descid, desc = httpGet(hostaddress, s, 'lcc')
      # (Applies to physical deployments only.) Information about memory modules in the storage system.
      if (module.lower() == 'memorymodule'):
         value, descid, desc = httpGet(hostaddress, s, 'memoryModule')
      # (Applies to physical deployments only.) Information about power supplies in the storage system.
      if (module.lower() == 'powersupply'):
         value, descid, desc = httpGet(hostaddress, s, 'powerSupply')
      # (Applies to physical deployments only.) Information about Serial Attached SCSI (SAS)
      # ports in the storage system. 
      if (module.lower() == 'sasport'):
         value, descid, desc = httpGet(hostaddress, s, 'sasPort')
      # (Applies to physical deployments only.) Information about System Status Cards (SSCs) in the storage system. 
      if (module.lower() == 'ssc'):
         value, descid, desc = httpGet(hostaddress, s, 'ssc')
      # (Applies to physical deployments only.) Information about internal Flash-based Solid
      # State Disks (SSDs, mSATAs) in the storage system. 
      if (module.lower() == 'ssd'):
         value, descid, desc = httpGet(hostaddress, s, 'ssd')
      # Information about Storage Processors (SPs) in the storage system.
      if (module.lower() == 'storageprocessor'):
         value, descid, desc = httpGet(hostaddress, s, 'storageProcessor')
      # (Applies to physical deployments only.) Information about Uncommitted ports in the storage system.
      if (module.lower() == 'uncommittedport'):
         value, descid, desc = httpGet(hostaddress, s, 'uncommittedPort')

      s.post('https://'+hostaddress+'/api/types/loginSessionInfo/action/logout', data=json.dumps({'localCleanupOnly': 'true'}))
      j = json.loads(r.text)
      #return j['logout']

   else:
      value  = 0
      descid = 'COULD_NOT_LOGIN'
      desc   = 'Could not login on REST url'
      
   
   if (value or value == 0) and descid and desc:
      s_nagios, s_msg1, s_msg2, s_val, s_exit = NagiosStatus(value, descid, desc)
      print ('%s: %s,%s,%s' % (s_nagios,s_msg1,s_msg2,s_val))
      sys.exit(s_exit)
   sys.exit(0)


if __name__ == '__main__':
   main()
