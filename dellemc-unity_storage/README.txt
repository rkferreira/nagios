### check_unity.py ###

This is a Nagios monitoring script for DELL EMC Unity storage box.


[root@]# ./check_unity2.py -H myunitybox.foo.com -u monituser -p monitpass -m <module>
usage: check_unity2.py [-h] -H HOSTADDRESS -u USER -p PASSWORD -m
                       {battery,dae,disk,dpe,ethernetport,fan,fcport,iomodule,lcc,memorymodule,powersupply,sasport,ssc,ssd,storageprocessor,system,uncommittedport}
check_unity2.py: error: argument -m/--module is required
 

[root@]# ./check_unity2.py -H myunitybox.foo.com -u monituser -p monitpass -m system
OK: ALRT_SYSTEM_OK,The system is operating normally.,5
