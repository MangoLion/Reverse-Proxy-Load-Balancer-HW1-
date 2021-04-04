
import socket
import json

#parse commandline arguments
import sys
it = iter(sys.argv[1:])
for opt in it:
    arg = next(it)
    if opt == '-id':
        SOURCE_PORT = int(arg)
    elif opt == '-revproc':
        PORT = int(arg)
    elif opt == '-pkt':
        pkt_filename = arg

#open and parse json package
pkt_file = open(pkt_filename,)
pkt = json.load(pkt_file)

HOST = '127.0.0.1'  # The server's hostname or IP address

#override with clientID from arguments
pkt['srcid'] = SOURCE_PORT
pkt_str = json.dumps(pkt)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, SOURCE_PORT))
    s.connect((HOST, PORT))

    print("Sending message {} to privacy policy {} through reverse proxy running on port {}".format(pkt['payload'], pkt['privPoliId'], PORT))
    s.sendall(pkt_str.encode())
    data = s.recv(1024)
    pkt = json.loads(data.decode("utf-8"))
    print("Receiving a response from the server {} payload: {}".format(pkt["srcid"], pkt["payload"]))

