import socket
import sys
import thread
import json

HOST = ''
PORT = 9888
print """
    Live Threaded Server - open socket and wait for connection.
    Reply in a thread.
    Repeat.
    """

world = {'this':1.23,
         'that':'blah',
         'other':[1,2,3,4.0,'frff'],
         'connects':0,
         'message':'',
         }

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
    s.bind((HOST, PORT))
except socket.error, msg:
    print 'FAILED to bind. Error :',msg[0], 'Message', msg[1]
    sys.exit()

print 'binding done'

s.listen(10)
print 'socket now listening'

while 1:
    print 'waiting..'
    conn, addr = s.accept()
    print 'Connected with',addr[0],':',addr[1]

    thread.start_new_thread(clientThread, (conn, addr))

s.close()
