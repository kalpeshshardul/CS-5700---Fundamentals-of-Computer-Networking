import socket #Impoeted the Socket Library
import re   #Imported the Regex Libraray
import sys  #Imported the sys Libraray
from bs4 import BeautifulSoup   #Imported Beautifulsoup from bs4 folder

def error():        #This socket connection will be established when the program will face IndexError
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('cs5700sp16.ccs.neu.edu', 80))
    s.send("GET /accounts/login/?next=/fakebook/ HTTP/1.1\r\nHost: cs5700sp16.ccs.neu.edu\r\n\r\n")
    a = s.recv(4096)
    token = re.findall(r'csrftoken=(\w+)', a, re.I)
    sid = re.findall(r'sessionid=(\w+)', a, re.I)
    p1 = "POST /accounts/login/ HTTP/1.1\r\n"
    p2 = "Host: cs5700sp16.ccs.neu.edu\r\n"
    p3 = "Cookie: csrftoken="+token[0]+"; sessionid="+sid[0]+"\r\n"
    p4 = "Content-Length: 109\r\n\r\n"
    p5 = "username="+uname+"&password="+pword+"&csrfmiddlewaretoken="+token[0]+"&next=%2Ffakebook%2F"
    p = p1+p2+p3+p4+p5
    s.send(p)
    b = s.recv(4096)
    newsid = re.findall(r'sessionid=(\w+)', b, re.I)

uname = sys.argv[1]     #USERNAME extracted from input
pword = sys.argv[2]     #PASSWORD extracted from input

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       #Socket
s.connect(('cs5700sp16.ccs.neu.edu', 80))                   #Socket connect request
s.send("GET /accounts/login/?next=/fakebook/ HTTP/1.1\r\nHost: cs5700sp16.ccs.neu.edu\r\n\r\n")     #Send the socket  to server with GETmessage to getthe website headers
a = s.recv(4096)        #Receive data from server
token = re.findall(r'csrftoken=(\w+)', a, re.I)     #Search csrftoken from the received headers
sid = re.findall(r'sessionid=(\w+)', a, re.I)       #Search sessionid from the received headers
p1 = "POST /accounts/login/ HTTP/1.1\r\n"
p2 = "Host: cs5700sp16.ccs.neu.edu\r\n"
p3 = "Cookie: csrftoken="+token[0]+"; sessionid="+sid[0]+"\r\n"
p4 = "Content-Length: 109\r\n\r\n"
p5 = "username="+uname+"&password="+pword+"&csrfmiddlewaretoken="+token[0]+"&next=%2Ffakebook%2F"
p = p1+p2+p3+p4+p5
s.send(p)       #Sent a post request with all parameters
b = s.recv(4096)
newsid = re.findall(r'sessionid=(\w+)', b, re.I)            #Extracted new sessionid from the received data

i=0
urls = ['/fakebook/']           #URLs to be visited will be stored here
visited = ['http://www.ccs.neu.edu/home/choffnes/', 'http://www.northeastern.edu', 'mailto:choffnes@ccs.neu.edu']       #Visited pages will be stored here

while len(urls) > 0:            #If the number of URLs left is greater than 0 then this will run else it will terminate
    if urls[0] not in visited:      #This check whether the URL to be visited is not a VISITED url
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('cs5700sp16.ccs.neu.edu', 80))
        try:
            session = "GET "+urls[0]+" HTTP/1.1\r\nHost: cs5700sp16.ccs.neu.edu\r\nCookie: csrftoken="+token[0]+"; sessionid="+newsid[0]+"\r\n\r\n"
        except IndexError:
            error()
            session = "GET "+urls[0]+" HTTP/1.1\r\nHost: cs5700sp16.ccs.neu.edu\r\nCookie: csrftoken="+token[0]+"; sessionid="+newsid[0]+"\r\n\r\n"
        s.send(session)
        c = s.recv(4096)
        flag=re.findall(r'FLAG: (\w*)',c, re.I)         #Search for secret flag in the source code of the webpage
        if flag != []:          #If flag is not empty then enter the loop
            i=i+1
            print flag[0]           #Print flag
            if i == 5:
                s.close()           #Close the socket if all flags are received
                exit()              #Exit the program
        
        if c[0:12] == 'HTTP/1.1 200':           #If header is HTTP/1.1 200 OK them it will enter in this loop
            #soup = BeautifulSoup(c)             #BeautifulSoup breaks the source code into parts
            pattern1 = re.compile(r'<a href=\"(/fakebook/[a-z0-9/]+)\">')
            links = pattern1.findall(c)
                              
	     visited.append(links[0])             #After visiting a URL, it will be added to VISITED urls
            links.pop(0)                         #Remove the visited URL from the list
            for tag in soup.findAll('a', href=True):        #Finding <a> tags in source code
                if tag['href'] not in visited:              #If URL not visited then add to URLS
                    urls.append(tag['href'])
        elif c[0:12] == 'HTTP/1.1 301':             #Handles the 301 HTTP Code
            urls[0]=c.split('\r\n')[5][39:]         #Extracted the new redirect address
            continue
        elif c[0:12] == 'HTTP/1.1 404':             #Handles the 404 HTTP Code, PAGE NOT FOUND
            urls.pop(0)
            continue
        elif c[0:12] == 'HTTP/1.1 500':              #Handles the 500 HTTP Code, INTERNAL SERVER ERROR
            continue
        else:
            urls.pop(0)
            continue


    else:
        urls.pop(0)             #If URL already visited, it will remove it from the list and once again try to request the next webpage.
I
