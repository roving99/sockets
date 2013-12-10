import socket
import sys
import thread
import json
import time

HOST = ''
PORT = 9888
print """
    Client Server BASIC - open socket and wait for connection.
    Send message.
    Get message.
    """

def clientThread(conn, addr):
    global world
    conn.sendall(json.dumps([world,]))      # ALWAYS return a list
    while True:
        data = conn.recv(1024)
        if not data:
            break
        try:
            j = json.loads(str(data))
        except:
            conn.sendall(json.dumps(['ERROR']))      # ALWAYS return a list
        else: 
            if type(j)==dict:
                for key in j.keys():
                    if key in world.keys():
                        world[key] = j[key]
            conn.sendall(json.dumps([world,]))      # ALWAYS return a list
            world['connects'] = world['connects']+1

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

while 1:
#    thread.start_new_thread(clientThread, (conn, addr))
    s.send("[]")
    data = s.recv(1024)
    print data
    time.sleep(0.05)
s.close()
