import socket
import sys
import thread

HOST = ''
PORT = 9888
print """
    Live Threaded Server - open socket and wait for connection.
    Reply in a thread.
    Repeat.
    """

def clientThread(conn, addr):
    conn.send('Welcome. Type shit. Get it echod')
    while True:
        data = conn.recv(1024)
        reply = 'OK : '+str(data)
        if not data:
            break
        conn.sendall(reply)
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
