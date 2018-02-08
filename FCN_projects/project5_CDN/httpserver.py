#! /usr/bin/python

import socket,urllib2,sqlite3,zlib,os,sys
import subprocess
###############################################TO GET THE IP of the HOST MACHINE####################################################
def getmyip():
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip
#################################TO VERIFY THE ORDER OF THE GIVEN ARGUMENTS IN THE COMMAND LINE######################################
try:
  if len(sys.argv) == 5 and sys.argv[1] == '-p' and sys.argv[3] == '-o' and int(sys.argv[2]) > 40000 and int(sys.argv[2]) < 65000:
     port = int(sys.argv[2])
     origin = sys.argv[4]

except IndexError:
    sys.exit('Please Use the format "./httpserver -p <port> -o <origin>"')

sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((getmyip(), int(port))) #Binding the UDP Socket to the given port
print 'The HTTP Server is Up and Running'
#################################################REQUESTING THE WEB PAGE###########################################################
def request_origin():
        url = 'http://'+origin+':8080/'+Path
        response = urllib2.urlopen(url)
        global webContent
        webContent = response.read()
        return webContent
############################################TO GET THE CONTENT FROM THE CACHE#####################################################
def content_from_cache():
        contentobj = d.execute("SELECT Data FROM CACHE WHERE Path =:Path",{"Path":Path})
        content = d.fetchone()
        hitsobj = d.execute("SELECT Count FROM CACHE WHERE Path =:Path",{"Path":Path})
        Hits = d.fetchone()
        Hits = Hits[0]
        Hits = Hits + 1
        content = zlib.decompress(content[0])
        conn.send(headen + content)
        d.execute("UPDATE CACHE SET Count =:Hits WHERE Path=:Path",{"Hits":Hits,"Path":Path})
############################################INSERTING THE CONTENT IN THE DATABASE#################################################
def insert_content():
        d.execute("INSERT INTO CACHE(Path,Count,Data) VALUES(?,?,?)",(Path,count,data))
while True: #While loop starts here
    sock.listen(1)
    conn,addr = sock.accept()
    data = conn.recv(1024)
    data =data.split('\n')
    gettillhttp = data[0]
    Path = gettillhttp[5:-10]
    header = 'HTTP/1.1 200 OK\r\n\r\n'
    wrongheader = 'HTTP/1.1 404 Not Found\r\n\r\n'
    headen = header.encode()
    wrongheaden = wrongheader.encode()

    try:
        file = open(Path,'r')

    except IOError:
        try:
            db = sqlite3.connect('htmlcache.db')
            d = db.cursor()
            d.execute('''CREATE TABLE IF NOT EXISTS CACHE
             (Path TEXT ,Count INT, Data BLOB);''')
            pathobj = d.execute("SELECT Path FROM CACHE WHERE Path =:Path",{"Path":Path})
            link = d.fetchone()
            if link == None:
                    request_origin()
                    data = buffer(zlib.compress(webContent))
                    conn.send(headen + webContent)
                    count = 1
                    disk_size_output = int(subprocess.check_output("du -b|tail -1| cut -f1",shell = True))
                    websize=len(webContent)
                    total_size=(disk_size_output+websize)/(1024.0*1024.0)
                    print "The total size is ", total_size
                    if (total_size < 9.5):
                        insert_content()
                    else:
                        d.execute("DELETE FROM CACHE WHERE Path = (SELECT Path FROM CACHE WHERE count = (SELECT MIN(count) FROM CACHE))")
                        insert_content()
            else:
                print "Taking the content from cache database"
                content_from_cache()

            db.commit()
            conn.close()

        except urllib2.HTTPError:
            conn.send(wrongheaden+"404 WEBPAGE FOUND.PLEASE CHECK THE WEBPAGE AGAIN") #If exception is generated in the program
            conn.close()