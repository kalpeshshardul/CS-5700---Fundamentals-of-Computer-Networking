#!/usr/bin/python

import socket,sys,threading,struct,math,collections,urllib,urllib2,json
from thread import *
###############################################################HEADER DETAILS#######################################################
global dns_response

def head_construct(ident): #Constructing header
        flag = '\x81\x80'
        qd = q_header[2]
        an = 1
        ns = 0
        ar = 0
        Head = struct.pack('!H', ident) + flag + struct.pack('!4H', qd, an, ns, ar)
        return Head

def ans_construct(best_replica): #Construction of answer
        name = 0xc00c
        type = 0x0001
        clas = 0X0001
        ttl = 60
        rd_length = 0x0004
        r_data = socket.inet_aton(best_replica)

        Ans = struct.pack('!HHHLH4s', name, type, clas, ttl, rd_length, r_data)
        return Ans
##########################################################EC2 REPLICAS USING GEO-LOCAION#################################################
def search_best_replica(address): #Searching the best replica out of the nine replicas for the requesting clients with the help of Geo Location 

        EC2_Hosts_IP = ['54.233.152.60','52.90.80.45','52.28.249.79','52.215.87.82','52.62.198.57','52.192.64.163','54.70.111.57','54.169.10.54','54.183.23.203']
        coordinates = collections.OrderedDict()                   # Inserting EC2_Hosts latitude and longitude values in an ordered dictionary
        results=list()

        Value=((urllib2.urlopen('http://api.ipinfodb.com/v3/ip-city/?key=d681cbf298b459b62d2313e03b1333355f38ebb46e5f742896b144b4c385802f&ip=' + address)).read()).split(';')
        x_cord = (90.0 - float(Value[8]))*0.0174532925199     #Latitude value for client
        y_cord = (0.0174532925199*(float(Value[9])))  #Longitube value for client

        coordinates['Sao_Paulo'] = [-46.6361, -23.5475]
        coordinates['N.Virginia'] = [-77.4875, 39.0437]
        coordinates['Frankfrut'] = [8.6841, 50.1155]
        coordinates['Ireland'] = [-6.2671, 53.3439]
        coordinates['Sydney'] = [151.2073, -33.8678]
        coordinates['Tokyo'] = [139.6917, 35.6895]
        coordinates['Oregon'] = [-122.6762, 45.5235]
        coordinates['Singapore'] = [103.8500, 1.2896]
        coordinates['N.California'] = [-122.4194, 37.7749]

        for item in coordinates:
                distance = (math.sin(0.0174532925199*(90.0 - coordinates[item][1]))*math.sin(x_cord)*math.cos(0.0174532925199*(coordinates[item][0])-y_cord)+math.cos(0.0174532925199*(90.0 - coordinates[item][1]))*math.cos(x_cord))
                arc_distance = (math.acos(distance))*3959        # Using Haversine formula to find the arc distance between coordinates of client and server and converting into miles by multiplying it by 3959
                results.append(arc_distance)
        print "The best ip is", EC2_Hosts_IP[results.index(min(results))] #Prints the nearest replica for the requesting client
        return EC2_Hosts_IP[results.index(min(results))]


def quest_construct(Q):              # DNS Question Header

        initial = list()
        name =''
        start=12
        diff=ord(Q[start])
        while diff!=0:                         # Extracting the Hostname 
                var=Q[start+1:start+diff+1]
                initial.append(var)
                start=start+diff+1
                diff=ord(Q[start])

        for item in initial:
                name += item + '.'

        return Q[12:start+5],name[:-1]

def execute(query,sock):

        while True:

                DQ = query[0]
                global q_header
                q_header = struct.unpack('!HHHHHH', DQ[:12])        # Extract Header Question in repect to the generated ID number
                global ident
                ident = q_header[0]
                question,var = quest_construct(DQ)
                dns_response = head_construct(ident) + question + ans_construct(search_best_replica(query[1][0]))

                sock.sendto(dns_response,query[1])         # Sending the DNS response to the client
                sys.exit()
###################################################THE MAIN FUNCTION#######################################################
def Main():                 # Defining main function

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                 # Socket creation
        sock.bind(('',p_num))

        while True:                                                                 # Handling client request
                incoming_request = sock.recvfrom(62000)
                new_request = threading.Thread(target=execute,args=(incoming_request,sock))   # Creating thread for each new request
                new_request.start()

if sys.argv[1]=='-p' and sys.argv[3]=='-n':                    # Check Args are correct or not on command line

        try:
                if int(sys.argv[2])>= 40000 and int(sys.argv[2])<=65535:           # Checking for the valid port number
                        p_num = int(sys.argv[2])
                else:
                        print "Port range should be between 40000 to 65535"

                        
        except ValueError:
                print "Wrong Port Number"
                sys.exit()
else:
        print "Wrong arguments:Follow format: ./dnsserver -p <port> -n <name>"
        sys.exit()

if __name__=='__main__':                  # Calling on main function            
        Main()