### check_unity.py ###

This is a Nagios monitoring script for DELL EMC Unity storage box.


[root@]# ./check_unity2.py -H myunitybox.foo.com -u monituser -p monitpass -m <module>
usage: check_unity2.py [-h] -H HOSTADDRESS -u USER -p PASSWORD -m
                       {battery,dae,disk,dpe,ethernetport,fan,fcport,iomodule,lcc,memorymodule,powersupply,sasport,ssc,ssd,storageprocessor,system,uncommittedport}
check_unity2.py: error: argument -m/--module is required
 

[root@]# ./check_unity2.py -H myunitybox.foo.com -u monituser -p monitpass -m system
OK: ALRT_SYSTEM_OK,The system is operating normally.,5


** Currently running and tested on RHEL5/Centos5 (python26):
    python26-requests-0.13.1-1.el5
    python26-argparse-1.2.1-3.el5
