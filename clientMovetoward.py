import messaging
import time
import math
import maps

def pretty(p):	# pretty text verion of pose
    result = "( "
    for n in p:
        result += "%3.3f, "%(float(n))
    result = result[:-2]+" )"
    return result

port = 5558

client = messaging.Client(port)

running = True

target = [50,50,math.pi/2]

client.send('MOVE',[0,0])		# ALL STOP
topic, message = client.recv()
client.send('RESET',[])			# Reset Pose
topic, message = client.recv()
time.sleep(0.1)
client.send('RESET',[])			# Reset Pose
topic, message = client.recv()
time.sleep(0.1)

client.send('pose',[])
topic, message = client.recv()
print "INITIAL POSE :",pretty(eval(message))
print " TARGET POSE :",pretty(target)

while running: 
    client.send('pose',[])
    topic, message = client.recv()
    pose = eval(message)
    bearing = maps.drect(pose, target)
    dtheta = maps.dtheta(pose[2], bearing[1])
    print pretty(pose), "\t", pretty(target), "\t", pretty(bearing), "\t%3.3f"%(dtheta)
    if abs(bearing[0])<1: # within 1cm of target?
        client.send('MOVE',[0.0, 0.0])
        topic, message = client.recv()
        running = False
    else:
        if abs(dtheta)>0.1:	# not pointing in the right direction?
            if dtheta<0:
                client.send('MOVE',[0.0, 0.2])
                client.recv()
            else:
                client.send('MOVE',[0.0, -0.2])
                client.recv()
        else:	# head toward target
	    client.send('MOVE',[0.4, 0.0])
            client.recv()
    time.sleep(0.1)
    
'''
client.send('MOVE',[0,0])		# ALL STOP
topic, message = client.recv()
'''

print
print "exited"
