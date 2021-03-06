import socket
import sys
import thread
import json
import time

HOST = ''
PORT = 9888
print """
    Client Server Threaed - open socket and poll for 'world' data.
    Main loop print world every 0.5s.
    Thread updates every 100mS.
    """

world = [{},]

def clientThread(s):
    global world
    while True:
        s.send("[]")
        data = s.recv(1024)
        if not data:
            break
        try:
            j = json.loads(str(data))
        except:
            print 'bad data :',data
        else: 
            world = j

        time.sleep(0.1)

    print addr[0],':',addr[1], 'disconnected'
    conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'created socket'

try:
    s.connect((HOST, PORT))
except socket.error, msg:
    print 'FAILED to connect. Error :',msg[0], 'Message', msg[1]
    sys.exit()

print 'Connected to', HOST,':', PORT
print 'starting threaded cleint.'
thread.start_new_thread(clientThread, (s,))

while 1:
    print world
    if 'connects' in world[0].keys():
        print world[0]['connects']
    print
    time.sleep(0.5)
