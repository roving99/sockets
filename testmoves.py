#!/usr/bin/python
# ./testmoves.py

import sys
import time
import messaging

port = "5558"
port = int(port)
times = 1
'''
if len(sys.argv) < 3:
    print "sendserver <port> <topic> <message>"
    print
    print "send topic, message to server."
    print
    sys.exit()
port =  sys.argv[1]
port = int(port)
topic = sys.argv[2]
message = sys.argv[3]
'''

# Socket to talk to server
client = messaging.Client(port)

t = time.time()
client.send('all',[])
topic, message = client.recv()
print topic, message, time.time()-t
data = eval(message)
pose = data['pose']
print pose

