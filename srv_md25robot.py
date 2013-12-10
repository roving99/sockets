#!/usr/bin/python
# 0MQ server - gets data from md25 robot and servers on 5557

import random
import sys
import time
import math
import copy
import json

import messaging
import md25

def server_worker(caller, conn, addr, message):  # run when server gets a client request.
    print 'worker'
    global running
    global world
    try:
        j = json.loads(str(message))
    except:
        return json.dumps(['ERROR', "improperly structred message %s"%(message)])      # ALWAYS return a list
    else:
        print j, type(j)
        if type(j)==dict:
            for key in j.keys():
                if key in world.keys():
                    world[key] = j[key]
        if type(j)==unicode:
            if j in [u'__KILL__', ]:
                if j==u'__KILL__':
                    running = False
                    return json.dumps(['ERROR','KILLED'])      # ALWAYS return a list

    return json.dumps([world])      # ALWAYS return a list

HOST = ''
PORT = 9888

m=md25.Md25()
world = m.get('all', True)

print "Starting server on %s:%s." % (HOST, PORT)

server = messaging.ServerThread(HOST, PORT, 'srv_md25', world, server_worker)        # Threaded server.

running = True
command  = ''

server.start()

i = 0
while running:
    t = time.time()
    m.move(world['motion'][0],world['motion'][1])
    data = m.get('all', True)   # True = re-poll Arduino for fresh data.
    world = data
    time.sleep(0.1)
    i +=1

server.stop()
