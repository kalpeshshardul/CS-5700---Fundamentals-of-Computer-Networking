High-Level Approach:

We have designed this code using Python language as we re more familiar and experienced in working on it.
First we import the socket and initialize it to a TCP connection and to accepted the IPv4 addresses. After we connect to the cs5700sp16.ccs.neu.edu we try to GET the login page (/accounts/login/?next=/fakebook/). Once we are directed to this page we by the use of the POST enter in the user’s credentials: Username and Password along with the Host, Cookie (csrftoken, session id) and Content-Length.
To get the headers which we to be sent with the GET and POST request were extracted by doing reverse engineering and observing the headers using Chrome Developer Tools.
After logging in web page another GET request was sent to get the required webpage to crawl. After the page is received the crawler tries to search for all the <a> tags in the source code of the webpage and extracts all the links which have "href=True". Two different queues were created by name URLS and VISITED. The URLS keeps the database of all the links which are yet to be visited, and VISITED keeps a track of all the Visited links. The extracted links were stored temporarily in a "tag" string which then checks every link whether it is stored in links already VISITED or not.
After extracting the links, the program sends the GET request to get the next page. The URL present at the 0th position will be used to send the request. After visiting the page the URL will be added to the VISITED queue, and it will be removed from URLS and this process goes on.

Challenges:

1. The syntax for the GET, POST and the parameters to be passed  were initially very difficult to handle as we have never handled them before. 
2. The server was randomly sending INTERNAL SERVER ERROR which needs to be taken care as it would terminate the connection if ignored.
3. Sometimes no token is received from the server due to which IndexError was appearing again and again. An exception was added to take care of that. 


Testing the code: 

The code was tested using PyCharm and we were able to get all the five secret flags without any errors but there were some problems when the code was tested on CCIS machine, which were later resolved. The code was working perfectly fine on PyCharm, CCIS Machine and Linux Terminal.

