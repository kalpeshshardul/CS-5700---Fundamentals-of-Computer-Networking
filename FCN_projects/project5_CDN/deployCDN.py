#!/usr/bin/python
import sys
import subprocess
#################################################################NICE EC2 REPLICAS#############################################################
replicas = ["ec2-52-90-80-45.compute-1.amazonaws.com",
"ec2-54-183-23-203.us-west-1.compute.amazonaws.com",
"ec2-54-70-111-57.us-west-2.compute.amazonaws.com",
"ec2-52-215-87-82.eu-west-1.compute.amazonaws.com",
"ec2-52-28-249-79.eu-central-1.compute.amazonaws.com",
"ec2-54-169-10-54.ap-southeast-1.compute.amazonaws.com",
"ec2-52-62-198-57.ap-southeast-2.compute.amazonaws.com",
"ec2-52-192-64-163.ap-northeast-1.compute.amazonaws.com",
"ec2-54-233-152-60.sa-east-1.compute.amazonaws.com"]

dns_server = "cs5700cdnproject.ccs.neu.edu"

##################################################READ THE ARGUMENTS IN THE CORRECT FORMAT####################################################
if len(sys.argv) == 11 and sys.argv[1] == '-p' and sys.argv[3] == '-o' and sys.argv[5] == '-n' and sys.argv[7] == '-u' and sys.argv[9] == '-i' :
        serverport = int(sys.argv[2])
        originserver = str(sys.argv[4])
        nameserver = str(sys.argv[6])
        username = str(sys.argv[8])
        key_file = str(sys.argv[10])
else:
        print "Improper arguments"
###############################################################HTTPSERVER#####################################################################
for each_replica in replicas:

        process_scp = subprocess.Popen("scp -i "+key_file+" httpserver "+username+"@"+each_replica+":~",shell=True,stdout=subprocess.PIPE)
        pro_op_scp = process_scp.communicate()[0]
        print "SCP Done HTTP"
        process_ssh = subprocess.Popen("ssh -i "+key_file+" "+username+"@"+each_replica+" chmod 755 httpserver",shell=True,stdout=subprocess.PIPE)
        pro_op_ssh = process_ssh.communicate()[0]
        print "SSH Done HTTP"

###############################################################DNSSERVER######################################################################
dns_scp = subprocess.Popen("scp -i "+key_file+" dnsserver "+username+"@"+dns_server+":~",shell=True,stdout=subprocess.PIPE)
process_scp = dns_scp.communicate()[0]
dns_ssh = subprocess.Popen("ssh -i "+key_file+" "+username+"@"+dns_server+" chmod 755 dnsserver",shell=True,stdout=subprocess.PIPE)
process_ssh = dns_ssh.communicate()[0]

print "The deploy is sucessfull!!"