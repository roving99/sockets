import socket
import sys
import thread
import json
import time
import maps
import messaging

HOST = ''
PORT = 9888
PORT_MAPPING = 9889

print """
    Mapping Server Threaded 
    - open socket and poll for 'world' data.
    - maintain a map
    - update using sonar data 
    Main loop print world every 0.5s.
    Thread updates every 100mS.
    """

worldMap = maps.SonarMap()

def server_worker(caller, conn, addr, message):  # run when server gets a client request.
    print 'worker'
    global running
    global worldMap
    try:
        j = json.loads(str(message))
    except:
        return json.dumps(['ERROR', "improperly structred message %s"%(message)])      # ALWAYS return a list
    else:
        print j, type(j)
        if type(j)==unicode:
            if j in [u'__KILL__', ]:
                if j==u'__KILL__':
                    running = False
                    return json.dumps(['ERROR','KILLED'])      # ALWAYS return a list

    return json.dumps([worldMap.list()])      # ALWAYS return a list


print "Creating server on %s:%s"%(HOST,PORT_MAPPING)

server = messaging.ServerThread(HOST, PORT_MAPPING, 'srv_mapping', worldMap, server_worker)        # Threaded server.

print "Connecting to %s:%s"%(HOST,PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'created socket'

try:
    s.connect((HOST, PORT))
except socket.error, msg:
    print 'FAILED to connect to srv_md25. Error :',msg[0], 'Message', msg[1]
    sys.exit()

print 'Connected to', HOST,':', PORT
print 'Starting server'
server.start()
print 'starting Mapping main loop...'

while 1:
    s.send(json.dumps([]))
    data = s.recv(1024)
    try:
        j = json.loads(str(data))    # returns LIST
    except:
        print "Bad data :",j
    else:
        sonar = j[0]['sonar']
        heading = j[0]['pose'][2]
#        worldMap.updateAll(heading,sonar)
        worldMap.setAll(heading,sonar)
        print sonar
 
    time.sleep(0.5)
