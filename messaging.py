# publish/subscribe based on 0mq..

import time
from threading import Thread
import thread
import json
import socket


world = {'this':1.23,
         'that':'blah',
         'other':[1,2,3,4.0,],
         'connects':0,
         'message':'',
         'sum':0.0,
         }

class ServerThread(Thread):

    def __init__(self, host, port, name, env, func):

        Thread.__init__(self)   # always call __init__() !!
        '''
        name = name of this server
        env = data to serve
        func = function to call with args (self, message) when server recieves a request.
        '''
        self.port=port
        self.host=host
        self.name=name
        self.env = env
        self.func = func
        self.running = True
    '''
    def start(self):
        self.sock =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(10)
    '''
    def run(self):  # this is the code to run
        '''
        recieve incoming message, ansd pass to defined server worker.
        '''
        self.sock =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(10)

        self.running=True
        while self.running:
            print 'waiting..'
            conn, addr = self.sock.accept()
            print 'Connected with',addr[0],':',addr[1]

            thread.start_new_thread(self.clientThread, (conn, addr, self.func))

        s.close()

    def clientThread(self, conn, addr, func):
        while True:
            data = conn.recv(1024*4)
            if not data:
                break
            message = func(self, conn, addr, data)
            conn.sendall(message)
        print addr[0],':',addr[1], 'disconnected'
        conn.close()

    def stop(self):
        self.running = False

    def isRunning(self):
        return self.running

    def getEnv(self):
        return self.env

    def setEnv(self,env):
        self.env = env


class Server:

    def __init__(self, host, port, name, env):
        '''
        name = name of this server
        env = dict. enviroment
        '''
        self.port = port
        self.host = host
        self.name = name
        self.env = env
        self.conn = None
        self.addr = None
        self.start()

    def start(self):
        '''
        '''
        self.sock =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(10)

    def waitForConnection(self):
        self.conn, self.addr = self.sock.accept()

    def recv(self):
        if self.conn:
            string = self.conn.recv(1024*4)
            if not string:
                return None
        else:
            string = None
        return string

    def send(self, message):
        '''
        send a message 
        '''
        self.conn.sendall(message)

    def kill(self):
        self.conn.close()
        self.sock.close()


class Client:

    def __init__(self, host, port):
        self.port = port
        self.host = host
        self.start()

    def start(self):
        self.sock =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def recv(self):
        string = self.sock.recv(1024*4)
        return string

    def send(self, message):
        self.sock.send(message)

    def kill(self):
        self.sock.close()

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
            print 'close..'
            if j in [u'__KILL__', ]:
                print 'close..'
                if j==u'__KILL__':
                    print 'close..'
                    running = False
                    return json.dumps(['ERROR','KILLED'])      # ALWAYS return a list

    world['connects'] = world['connects']+1
    return json.dumps([world])

running = True

HOST = ''
PORT = 9888

if __name__=="__main__":
    s = ServerThread(HOST, PORT, 'test_server', world, server_worker)
#    s = Server(HOST, PORT, 'test', world)
    s.start()
    print "Running a server at %s:%s" % ( HOST, PORT)
    print
    i=0
    print 'Doing something else..'
    while running:
        print 'something'
        time.sleep(1)
    print "stopping server and publisher."
#    s.kill()
    print "ended."

