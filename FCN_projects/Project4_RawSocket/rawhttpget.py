#!/usr/bin/python
###################Importing the libraries required by the code
import socket
from urlparse import urlparse 
import sys
import random
from struct import *
import time
import os
import commands
###################using iptables to drop outgoing TCP RST packets
os.system("sudo iptables -F") 
os.system("sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP")

try:
    rawsock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806)) #CREATE SOCKET FOR SENDING THE ARP REQUEST
    rawsock.bind(('eth0' , 0x0806))
    rawsock_recv = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806)) #CREATE SOCKET FOR RECEIVING THE ARP REQUEST
except:
    print msg
    sys.exit()

try:
    sendpkt = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806))  #CREATE SOCKET FOR SENDING AND RECEIVING PACKET
    sendpkt.bind(('eth0' , 0x0806))
    recvpkt = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP) 
except:
    print msg
    sys.exit()

localmac_data = sendpkt.getsockname() #to get the mac address of the local machine
localmac = localmac_data[4] 
src_ip = socket.inet_aton((commands.getoutput('/sbin/ifconfig').split('\n')[0x01].split()[0x01])[5:])#source ip of the host
destinationIp = commands.getoutput('route -n').split('\n')[2].split()[0x01] #destination ip of the gateway for ARP request
destinationmac = ''
#############################Creating the ARP Header
ARP_HDR = pack('!2s2s1s1s2s','\x00\x01','\x08\x00','\x06','\x04','\x00\x01')
ARP_SENDER = pack('!6s4s', localmac, src_ip)
ARP_TARGET = pack('!6s4s', '\x00\x00\x00\x00\x00\x00',socket.inet_aton(destinationIp))
ETH1_HDR = pack('!6s6s2s', '\xff\xff\xff\xff\xff\xff',localmac,'\x08\x06')
while True:
	try:
            rawsock.send(ETH1_HDR + ARP_HDR + ARP_SENDER + ARP_TARGET)
            packet = rawsock_recv.recv(2048)
            ether = packet[0:14]
            arpdata = packet[14:42]  
            packet_header = arpdata[0:8]
            packet_sender = arpdata[8:18]
            packet_target = arpdata[18:28] 
            if unpack('!6s4s', packet_target)[0x01] == unpack('!6s4s',ARP_SENDER)[0x01]:
                if unpack('!6s4s', packet_sender)[0x01] == unpack('!6s4s', ARP_TARGET)[0x01]:
                        xyz = unpack('!2s2s1s1s2s6s4s6s4s',arpdata)
			destiantionmac = unpack('!6s4s',packet_sender)
			mac_gate = xyz[5]
                        break
	except:
		sys.exit()
########URLPARSE used to implement functionality same as wget with respect to the URL entered as argument	
s = socket.socket(socket.AF_INET,socket.SOCK_RAW, socket.SOCK_DGRAM)
dest_add = sys.argv[1]
o = urlparse(dest_add) #URLPARSE USED IN ORDER TO MAKE THE CODE ROBUST IN TERMS OF THE URL GIVEN AS ARGUMENT
path=o.path
scheme=len(o.scheme)
netloc=o.netloc
if scheme==0: #IF HTTP IS NOT PRESENT IN THE URL
	dest_add='http://' + dest_add
	if len(netloc)==0: #IF AFTER THE HOSTNAME THERE IS NO '/'
		dest_add = dest_add + '/'	
if path=='': 
	dest_add = dest_add + '/'
o = urlparse(dest_add)
path=o.path
x=os.path.basename(path) #THE PART OF URL REMAINING AFTER THE HOSTNAME
if len(x)==0:
	file_name = "index.html"
else:
	file_name = x

try:
	destination_name=socket.gethostbyname(o.netloc)
except socket.gaierror,msg:
	print "Please check the URL and try again, No address is associated with the given hostname" #incase of wrong url entered as argument
	sys.exit()

destination_ip=socket.inet_aton ( destination_name )
source_port = random.randint(3000,65535) #Random soruce port used by the random function 
dst_port = 80 #Port used for HTTP 
cwnd=0 #Initializing the congestion window as zero
###########################Calculation of checksum	
def carry_around_add(x, y):
    z = x + y
    return (z & 0xffff) + (z >> 16)
##########checksum functions needed for calculation checksum
def checksum(message):
    s = 0 
    if len(message)%2 != 0: #Since the loop takes two characters at a time
    	message=message+chr(0)
    	for i in range(0, len(message), 2):
        	w = ord(message[i]) + (ord(message[i+1]) << 8 )
        	s = carry_around_add(s,w)
    else:
     	for i in range(0, len(message), 2):
        	w = ord(message[i]) + (ord(message[i+1]) << 8 )
        	s = carry_around_add(s,w)
   #complement and mask to 4 byte short
    s = ~s & 0xffff 
    return s
#########################Constructing the packet############################################### 

#########################ETHERNET HEADER 

ethernet_hdr = pack('!6s6s2s', mac_gate,localmac,'\x08\x00')

#########################IP HEADER FIELDS
def ip_header(ip_id,ip_protocol,destination_ip,src_ip,ip_checksum,ip_tot_len):
	ip_headerlen = 5
	ip_version = 4
	ip_tos = 0
	ip_tot_len = ip_tot_len #total length
	ip_frag_off = 0
	ip_ttl = 255
	ip_protocol = socket.IPPROTO_TCP #Protocol used
	ip_checksum = ip_checksum   
	ip_headerlen_ver = (ip_version << 4) + ip_headerlen #Combining header length and ip version to make 8 bytes
	ip_header = pack('!BBHHHBBH4s4s' , ip_headerlen_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_protocol, ip_checksum, src_ip, destination_ip) #Packing the IP header
	return ip_header
	
#########################TCP HEADER FIELDS
def tcp_header(tcp_seq,tcp_ackno,tcp_ack,tcp_psh,tcp_syn,tcp_fin,user_data):
	tcp_source = source_port # source port
	tcp_dest = dst_port   # destination port
	tcp_ack_seq = tcp_ackno
	tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
	tcp_rst = 0 #TCP FLAGS
	tcp_urg = 0
	tcp_window = socket.htons (65535)    #   The advertised window present in the TCP header
	tcp_check = 0
	tcp_urg_ptr = 0
	tcp_offset_res = (tcp_doff << 4) + 0
	tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
	tcp_header=pack('!HHLLBBHHH',tcp_source,tcp_dest,tcp_seq,tcp_ack_seq,tcp_offset_res,tcp_flags,tcp_window,tcp_check,tcp_urg_ptr)# Packing the TCP header
 
#########################PSEUDO HEADER FIELDS
	reserved_pseudo = 0
	protocol = socket.IPPROTO_TCP
	tcp_length = len(tcp_header) + len(user_data) #sum of the tcp header and the data length
	psh=pack('!4s4sBBH',src_ip,destination_ip,reserved_pseudo,protocol,tcp_length);
	psh=psh+tcp_header + user_data;
	tcp_check = checksum(psh)	#calculating checksum of Pseudo header,tcp header and user data
	# make the tcp header again and fill the correct checksum in the header
	tcp_header = pack('!HHLLBBH',tcp_source,tcp_dest,tcp_seq,tcp_ack_seq,tcp_offset_res,tcp_flags,tcp_window)+pack('H',tcp_check)+pack('!H',tcp_urg_ptr)
	return tcp_header
########################Functions creared for different types of packets
def SYN():
	tcp_ackno=0	
	user_data=''
	ip_ident=random.randint(50000,60000)
	ip1_old=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,src_ip,0,40)
	ip1=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,src_ip,checksum(ip1_old),40)
	tcp_sequ=9999              #Manually hardcoded the sequence number as 9999
	tcp1=tcp_header(tcp_sequ,tcp_ackno,0,0,1,0,user_data)#Sending the SYN flag in the TCP header
	packet=ip1+tcp1 #Packet is comprised of ip header and tcp header
	final_packet = ethernet_hdr + packet #Final packet consists of the header(IP+TCP) and the Ethernet header
	sendpkt.send(final_packet) #Sending the SYN packet
	starting_time=time.time() #Start the time after sending the SYN flag
	SYN_ACK(starting_time) #Call the SYN_ACK function
	
def SYN_ACK(starting_time):
	receive_function() #calling the receive function 
	checksum=cal_rec_checksum(recd_packet)#Validating the checksum again and if correct will return zero
	if checksum==0:
		if tcp_flags==18 and ((starting_time-time.time())<60): 
			ACK(tcp_seqno,tcp_ackno) #Send the ACK for the corresponding received packet
		elif ((starting_time-time.time())>60):
			if ((starting_time-time.time())>180): #If no packet received then exit the program
				print "No packet in 3 minutes. Exiting"
				sys.exit()

def ACK(tcp_seqno,tcp_ackno):
	user_data='' #Data should be zero while sending an ACK
	ip_ident=random.randint(50000,60000) #Use of the random function
	ip1_old=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,src_ip,0,40)
	ip1=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,src_ip,checksum(ip1_old),40) #checksum calculated for the IP hader since we have also implemented ethernet header above it.
	#tcp_header(tcp_seq,tcp_ackno,tcp_ack,tcp_psh,tcp_syn,tcp_fin,user_data)		
	tcp1=tcp_header(tcp_ackno,tcp_seqno+1,1,0,0,0,user_data)
	packet=ip1+tcp1
        final_packet = ethernet_hdr + packet
	sendpkt.send(final_packet)
	GetData(tcp_ackno,tcp_seqno) #GET DATA function called after the handshake

def GetData(tcp_ackno,tcp_seqno):
	cwnd=0
	i=0
	starting_time=0
	ip_ident=random.randint(50000,60000)
	user_data = ("GET " +path+  " HTTP/1.0\r\n" #HTTP GET request
	"Host: david.choffnes.com\r\n"
	"Connection: keep-alive\r\n"
	"\r\n")
	user_data_len = len(user_data)
	if len(user_data) % 2 !=0:
		user_data = user_data + " " #To make the number of data bytes in even order
	ip1_old=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,src_ip,0,40+len(user_data))
	abcd = checksum(ip1_old) #IP Checksum calculation 
	ip1=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,src_ip,abcd,40+len(user_data))
	#tcp_header(tcp_seq,tcp_ackno,tcp_ack,tcp_psh,tcp_syn,tcp_fin,user_data)
	tcp1=tcp_header(tcp_ackno,tcp_seqno+1,1,1,0,0,user_data)
	tot_tcp_data=len(tcp1+user_data)-20
	packet=ip1+tcp1+user_data
        final_packet = ethernet_hdr + packet
	sendpkt.send(final_packet)
	final_data=()
	tcp_flags=0
	sequence_data={} #Creation of dictionary
	i = 0
	while True:
		recvd_data=recvpkt.recvfrom(65536)
		final_data+=recvd_data
		recvd_data=recvd_data[0]
		recd_packet=recvd_data[20:]
		ip_data=unpack('BBHHHBBH4s4s', recvd_data[0:20])
		ip_dst = socket.inet_ntoa(ip_data[8])
		ip_src = socket.inet_ntoa(ip_data[9])
		ip_version_headerl= ip_data[0]
		ip_version= ip_version_headerl >> 4
		IP_headerl= ((ip_version_headerl & 0xF) * 4)
		tcp_data= unpack('!HHLLBBHHH', recvd_data[IP_headerl : IP_headerl+20])
		tcp_seqno=tcp_data[2]
		tcp_ackno=tcp_data[3]
		tcp_flags = tcp_data[5]
		tcp_headerl_res = tcp_data[4]			
		tcp_headerl = tcp_headerl_res >> 4
		Total_Header = IP_headerl + (tcp_headerl *4)
		total_data = len(recvd_data) - Total_Header
		data=recvd_data[Total_Header:]
		checksumm=cal_rec_checksum(recd_packet)		
		if (tcp_data[0]==dst_port and tcp_data[1]==source_port): #Filtering wrt to source and destination port
			if i==0:
                  		i=i+1
				starting_time=time.time() #Start the timer
                        	added_seq=tcp_seqno+total_data #Calculating the sequence number
                        	prev_tcpseq=tcp_seqno #Database of previous seq and ack incase of some error
                        	prev_ack=tcp_ackno
                        	prev_totaldata=total_data
			else:
				if(added_seq==tcp_seqno and checksumm==0):
					if tcp_flags%2!=0:
						if tcp_flags==0x019: #When we receive FIN,PSH and ACK from the server	
							sequence_data[tcp_seqno]=data
							create_file(sequence_data)
							FIN_ACK(total_data,tcp_seqno,tcp_ackno)
									
						elif '301' in final_data[2] or '403' in final_data[2] or '500' in final_data[2] or '404' in final_data[2]: #Handelling the different kinds of HTTP status codes
							print"301 or 403 or 500 or 404 status code encountered"
							FIN_ACK(tcp_seqno,tcp_ackno)
							sys.exit()
						else:
							create_file(sequence_data)
							FIN_ACK(total_data,tcp_seqno,tcp_ackno)
					else:
						#To send the respective ACK for the data received from the server	
						sequence_data[tcp_seqno]=data
						ACK2(total_data,tcp_seqno,tcp_ackno)
						starting_time=time.time()
						added_seq=tcp_seqno+total_data
						prev_tcpseq=tcp_seqno
						prev_ack=tcp_ackno
						prev_totaldata=total_data
						if cwnd==1000:
							cwnd=1000
						else:
							cwnd+=1 #Increase the cwnd window linearly
				
				elif (added_seq!=tcp_seqno and ((time.time()-starting_time)> 180)):
					
					print "No packet in 3 minutes. Exiting."
					sys.exit()
				
				elif (added_seq!=tcp_seqno and ((time.time()-starting_time)>60)):
					#if timeout caused by the server, we again start the timer from zero
					starting_time=0 
					cwnd=1
					ACK2(prev_totaldata,prev_tcpseq,prev_ack)
					starting_time=time.time()

def ACK2(total_data,tcp_seqno,tcp_ackno):
	user_data=''
	ip_ident=random.randint(50000,60000)
	ip1_old=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,src_ip,0,40)
	#tcp_header(tcp_seq,tcp_ackno,tcp_ack,tcp_psh,tcp_syn,tcp_fin,user_data)
	ip1=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,src_ip,checksum(ip1_old),40)
	tcp1=tcp_header(tcp_ackno,tcp_seqno+total_data,1,0,0,0,user_data) #Sending the ACK flags in the packet
	packet=ip1+tcp1
        final_packet = ethernet_hdr + packet
	sendpkt.send(final_packet)

def FIN_ACK(total_data,tcp_seqno,tcp_ackno):
	user_data=''
	ip_ident=random.randint(50000,60000)
	ip1_old=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,src_ip,0,40)
	yyy=checksum(ip1_old)
	ip1=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,src_ip,yyy,40)
	#tcp_header(tcp_seq,tcp_ackno,tcp_ack,tcp_psh,tcp_syn,tcp_fin,user_data)
	tcp1=tcp_header(tcp_ackno,tcp_seqno+1,1,0,0,1,user_data) #Sending the FIN and ACK flags in the packet
	packet=ip1+tcp1
	final_packet = ethernet_hdr + packet
	sendpkt.send(final_packet)
	sendpkt.close()
	sys.exit()
###################################THE RECEIVE FUNCTION##############################
def receive_function():
        global recvd_data
	global recd_packet
        global tcp_seqno
        global tcp_ackno
        global tcp_flags
        global tcp_headerl_res
        global tcp_headerl
	recvd_data=recvpkt.recvfrom(65535)
	recvd_data=recvd_data[0]
        recd_packet=recvd_data[20:]
	ip_data=unpack('BBHHHBBH4s4s', recvd_data[0:20])
        ip_dst = socket.inet_ntoa(ip_data[8])
        ip_src = socket.inet_ntoa(ip_data[9])
        ip_version_headerl= ip_data[0]
        ip_version= ip_version_headerl >> 4
        IP_headerl= ((ip_version_headerl & 0xF) * 4)
        tcp_data= unpack('!HHLLBBHHH', recvd_data[IP_headerl : IP_headerl+20])
        tcp_seqno=tcp_data[2]
        tcp_ackno=tcp_data[3]
        tcp_flags=tcp_data[5]
        tcp_headerl_res = tcp_data[4]
        tcp_headerl = tcp_headerl_res >> 4
####################################Calculating the checksum again received in the packet
def cal_rec_checksum(recd_packet):
	protocol=socket.IPPROTO_TCP
	reserved_pseudo=0
	psh=pack('!4s4sBBH',src_ip,destination_ip,reserved_pseudo,protocol,len(recd_packet))
	psh=psh+recd_packet
	calc_checksum=checksum(psh)
	return calc_checksum
###################################Function to write data in a file	
def create_file(sequence_data):
	sorted_tcp_seq=sorted(sequence_data.keys()) # Sorting the data as per the sequence number 
	file=open(file_name,"w")
	i=0
	for j in sorted_tcp_seq:
		if i==0:
			data=sequence_data[j]
			file.writelines(data.split('\r\n\r\n')[1])
			i=i+1
		else:
			file.writelines(sequence_data[j])
	file.close()
################################FINAL EXECUTION OF THE FILE STARTS HERE
if (len(sys.argv)!=2):
	print "The argument entered is invalid"
	sys.exit()
else:
	SYN() #Start the program by sending an SYN Flag

