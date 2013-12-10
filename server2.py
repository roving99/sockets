import socket
import sys

HOST = ''
PORT = 9888
print """
    Live Server - open socket and wait for connection.
    Reply.
    Close socket.
    Repeat.
    """

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
    data = conn.recv(1024)
    print 'received', data
    reply = data
    
    if not data:
        break

    conn.sendall(str(reply))

conn.close()

s.close()
