#!/usr/bin/python
# Socket server - gets data from md25 robot and servers on 9888

import random
import sys
import time
import math
import copy
import json

import messaging
import md25


def rpc(j):     # perform rpc, return RPC dict
    id_ = j['id']
    method = j['method']
    params = j['params']
    result = {'result': None, 'error':4, 'id':id_}
    if method=='move':
        m.move(params[0], params[1])
        result['error'] = None
    if method=='stop':
        m.move(0., 0.)
        result['error'] = None
    if method=='reset':
        m.reset()
        result['error'] = None
    if method=='resetMap':
        m.newSonarMap()
        result['error'] = None
    if method=='get':
        if params=='all':
            result['result'] = m.get('all', False)  # do not refresh  
        if params=='sonarMapRect':
            result['result'] = m.get('sonarMapRect', False)  # do not refresh  
        result['error'] = None

    return result

def server_worker(caller, conn, addr, message):  # run when server gets a client request.
    """
    accepts JSON RPC Calls of form :
    {"method": "###", "params": [###], "id": ### }
    if id != null server MUST reply, quoting id.

    {"result": <any type>, "error":null, "id": ###}
    {"error": <error code>, "result":null, "id": ### }
    """
#    print 'worker'
    global running
    global world
    id_ = None
    try:
        j = json.loads(str(message))
    except:
        return json.dumps({"error": 1, "result": "Not a JSON string", "id":id_})      # ALWAYS return a dict
    else:
#        print j, type(j)
        if type(j)==dict:       # ONLY valid form
            if 'method' in j.keys() and 'params' in j.keys() and 'id' in j.keys():  # must have all three to be valid RPC 
                result = rpc(j)
                if result['id']!=None:
                    return json.dumps(result)
            else:
                return json.dumps({"error": 3, "result": "not a JSON RPC", "id":id_})      # ALWAYS return a dict
        else:
            return json.dumps({"error": 2, "result": "not a JSON dict", "id":id_})      # ALWAYS return a dict

    return json.dumps({"error": 3, "result": "not a valid method", "id":id_})      # ALWAYS return a dict

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
    data = m.get('all', True)   # True = re-poll for fresh data.
    world = data
    time.sleep(0.1)
    i +=1

server.stop()
