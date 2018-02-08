#!/usr/bin/python

import sys
import subprocess
import re

replicas = ["ec2-52-90-80-45.compute-1.amazonaws.com",
"ec2-54-183-23-203.us-west-1.compute.amazonaws.com",
"ec2-54-70-111-57.us-west-2.compute.amazonaws.com",
"ec2-52-215-87-82.eu-west-1.compute.amazonaws.com",
"ec2-52-28-249-79.eu-central-1.compute.amazonaws.com",
"ec2-54-169-10-54.ap-southeast-1.compute.amazonaws.com",
"ec2-52-62-198-57.ap-southeast-2.compute.amazonaws.com",
"ec2-52-192-64-163.ap-northeast-1.compute.amazonaws.com",
"ec2-54-233-152-60.sa-east-1.compute.amazonaws.com"]

#replicas = ["ec2-54-183-23-203.us-west-1.compute.amazonaws.com"]


dns_server = "cs5700cdnproject.ccs.neu.edu"

### read the arguments in correct format
if sys.argv[1] == '-p' and sys.argv[3] == '-o' and sys.argv[5] == '-n' and sys.argv[7] == '-u' and sys.argv[9] == '-i' :
        serverport = int(sys.argv[2])
        originserver = str(sys.argv[4])
        nameserver = str(sys.argv[6])
        username = str(sys.argv[8])
        key_file = str(sys.argv[10])

else:
        print "improper arguments"



print "Kill' 'em all the httpservers"
for each_replica in replicas:                           # kill the process httpserver for the particular username
        stop_httpserver = subprocess.Popen("ssh -i "+key_file+" "+username+"@"+each_replica+" pkill httpserver -u "+username,shell=True,stdout=subprocess.PIPE)
        stop_httpserver_op = stop_httpserver.communicate()[0]


print "Stopping DNS server.."
stop_dns = subprocess.Popen("ssh -i "+key_file+" "+username+"@"+dns_server+" pkill dnsserver -u "+username,shell=True,stdout=subprocess.PIPE)
stop_dns_op = stop_dns.communicate()[0]

print "Stopped all the processes"