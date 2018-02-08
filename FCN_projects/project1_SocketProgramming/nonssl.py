import socket               #import the modules
import re
import sys

port=int(sys.argv[1])                                           # This command will divide the input parameters into different words and select the corresponding word mentioned in the bracket by which that particular value can be imported.
host=sys.argv[2]                                                # This will import the data on the 2nd position of the input parameters and save it in host
nuid=sys.argv[3]                                                # This will import the data on the 3rd position of the input parameters and save it in nuid

if host=='cs5700sp16.ccs.neu.edu':
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)        #Create TCP/IP connection
    s.connect((host,port))                                      # Used to initiate the connection request.
    s.send('cs5700spring2016 HELLO'+' '+nuid+'\n')              # This command will send the data from the client to the server
    while 1:
        str1=s.recv(1024)                                       # This command will get the data from the server.
        if 'STATUS' in str1:
            a=(re.findall('\d+', str1 ))                        # This command will break the received command from the server into different parts
            m=a[2]
            o=a[3]
            if '+' in str1:
                p=int(m)+int(o)
            elif '-' in str1:
                p=int(m)-int(o)
            elif '*' in str1:
                p=int(m)*int(o)
            elif '/' in str1:
                p=int(m)/int(o)
            s.send("cs5700spring2016 "+str(int(p))+"\n")        #This command will send the data to the server from the client.
        elif 'BYE' in str1:
            print(str1)
            exit()                                              # Break and exit from the program
else:
    print('Unknown Host ID, Please check and Retry BYE')
    exit()
