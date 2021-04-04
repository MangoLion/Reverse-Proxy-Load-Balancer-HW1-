import os, socket
import json
import hashlib
from _thread import *
import threading
import sys

#parse commandline arguments
it = iter(sys.argv[1:])
for opt in it:
    arg = next(it)
    if opt == '-port':
        port = int(arg)

#policies dictionary, each key is a policy ID and 
#each value is a list of (serverID, server port) tuples, each tuple represents a server entry
policies = {}

#round robin counter dictionary, each key is a policy ID and each value is the current rr counter
rrCounters = {}

host="127.0.0.1"

#start the socket
s=socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen()

print("Running the reverse proxy on port ", port)

def handle_message(s, addr):
    while True:
        data=s.recv(1024)
        decoded_data=data.decode("utf-8")
        if not decoded_data:
            #break when connection close
            break

        #deserialize json
        pkt = json.loads(decoded_data)
        type = pkt["type"] 

        #register server with load balancer
        if type == 1:
            policyId = pkt["privPoliId"]
            #create new entry in policyIDs if policy ID is new
            if policyId not in policies:
                policies[policyId] = []
                rrCounters[policyId] = 0
            policies[policyId].append((pkt["id"],pkt["listenport"]))
            print("receiving setup message from server id " + str(pkt["id"])+ " privacy policy " + str(pkt["privPoliId"]) +  " port " + str(addr[1]))
        #use round robin to determine the server to serve
        elif type == 0:
            policyId = str(pkt["privPoliId"])
            print("Received a data message from client {} privacy policy {} payload: {}".format(pkt["srcid"], policyId, pkt["payload"]))
            counter = rrCounters[policyId]
            servers = policies[policyId]
            server = servers[counter % len(servers)]
            server_addr = server[1]
            print("Forwarding a data message to server id {} payload: {}".format(server[0],pkt["payload"]))
            s2=socket.socket()
            s2.connect((host, server_addr))
            s2.sendall(data)
            data=s2.recv(1024)
            pkt = json.loads(data.decode("utf-8"))
            print("Receiving a data message from server id {} payload: {}".format(server[0],pkt["payload"]))
            print("Forwarding a data message to client id {} payload: {}".format(server[0],pkt["destid"]))
            s.sendall(data)
            s2.close()

def server():
    while True:
        c, addr=s.accept()
        start_new_thread(handle_message, (c, addr))
server()