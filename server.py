import os, socket
import json
import hashlib
from _thread import *
import threading
import sys

#parsing arguments
it = iter(sys.argv[1:])
for opt in it:
    arg = next(it)
    if opt == '-id':
        ID = arg
    elif opt == '-pp':
        policyID = arg
    elif opt == '-listen':
        port = int(arg)
    elif opt =='-revproc':
        portRP = int(arg)

#init sha1 hash
sha_1 = hashlib.sha1()

print("Server running with id ", ID)
print("Server serving privacy policy ", policyID)
print("Listening on port ", port)

host="127.0.0.1"

#start a socket to send the setup message to the reverse proxy
s=socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
register_msg = json.dumps({
    "type":1,
    "id":ID,
    "privPoliId": policyID,
    "listenport": port
})
print("Connecting to the reverse proxy on port ", portRP)
s.connect((host, portRP))
s.sendall(register_msg.encode())
s.close()

#start a socket to start listening for client messages
s=socket.socket()
s.bind((host, port))
s.listen()

#process each client message
def handle_client(s, addr):
    data=s.recv(1024)
    decoded_data=data.decode("utf-8")

    #deserialize json
    pkt = json.loads(decoded_data)

    payload = pkt['payload']
    print("Received a message from client {} payload: {}".format(pkt["srcid"], payload))

    #hash payload and setup reply message
    sha_1.update(payload.encode())
    pkt['payload'] = sha_1.hexdigest()
    pkt['payloadsize'] = len(pkt['payload'])
    pkt['type'] = 2
    pkt['destid'] = pkt['srcid']
    pkt['srcid'] = port

    print("Sending a response to client {} payload: {}".format(pkt["destid"], pkt['payload']))
    s.sendall(json.dumps(pkt).encode())

#start the server
def server():
    while True:
        c, addr=s.accept()
        #make a new thread for each connection to allow multiple clients to connect at once
        start_new_thread(handle_client, (c, addr))
server()