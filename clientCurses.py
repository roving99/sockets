import messaging
import time
import curses as c
import json

gauges = {
    "Volts":  ['battery', 0, 2,0,  'number', 'v'],
    "Sonar F":['sonar',   0, 4,0,  'bar', 0,300],
    "Sonar L":['sonar',   1, 5,0,  'bar', 0,300],
    "Sonar R":['sonar',   2, 6,0,  'bar', 0,300],
    "Sonar B":['sonar',   3, 7,0,  'bar', 0,300],
    "bump L": ['bump',    0, 9,0,  'led'],
    "bump R": ['bump',    1, 9,10, 'led'],
    "cliffL": ['cliff',   0, 11,0, 'led'],
    "cliffR": ['cliff',   1, 11,10,'led'],
    "x":      ['pose',    0, 13,0, 'number', ' cm'],
    "y":      ['pose',    1, 13,15,'number', ' cm'],
    "theta":  ['pose',    2, 13,30,'number', ''],
    }

coordSystem = [ '         0          ',
		'         |          ',
		'        +x          ',
		'         |          ',
		'pi/2  +y . -y  -pi/2',
		'         |          ',
		'        -x          ',
		'         |          ',
		'      +pi -pi       ',
		]

def update(screen, data):
    for label in gauges.keys():
        line = gauges[label]
        key = line[0]
        i = line[1]
        y = line[2]
        x = line[3]
        type = line[4]

        if type=='number':
            text = label+" "+("%3.2f"%(float(data[key][i]))).rjust(6)+line[5]
            screen.addstr(y, x, text) 
        if type=='bar':
            p = float(data[key][i])/float(line[6])
            t = 40
            f = int(t*p)
            e = 40-f
            text = label+" "+("%3.2f"%(float(data[key][i]))).rjust(6)+" "+"#"*f+"-"*e
            screen.addstr(y, x, text) 
        if type=='led':
            text = label
            if data[key][i]:
                screen.addstr(y, x, text, c.A_REVERSE) 
            else:
                screen.addstr(y, x, text, c.A_DIM) 

    # coord system diagram
    y=15
    x=60
    for i in range(len(coordSystem)):
        screen.addstr(y+i,x,coordSystem[i])
    # raw data
    x = 1
    y = 25
    for key in data.keys():
        d = data[key]
        screen.addstr(y,x, str(key).rjust(10)+"  "+str(data[key]).ljust(40))
        y += 1


def main(screen, client):
    screen.addstr("MD25 robot control 0.1\n\n") 
    screen.nodelay(1)
    while True: 
        client.send(json.dumps([]))
        message = client.recv()
        data = json.loads(message)
        world = data[0]
        update(screen, world)
        event = screen.getch() 
        screen.addstr(15,0,str(event)+"   ")

        if event == ord("q"): break 

        tran = world['motion'][0]
        rot  = world['motion'][1]
        if event == 32:
            client.send(json.dumps({'motion':[0.0,0.0]}))		# ALL STOP
            message = client.recv()

        if event == 259 and tran<1.0:		# forward
            client.send(json.dumps({'motion':[tran+0.2,rot]}))		# ALL STOP
            message = client.recv()
        if event == 258 and tran>-1.0:		# reverse
            client.send(json.dumps({'motion':[tran-0.2,rot]}))		# ALL STOP
            message = client.recv()
        if event == 261 and rot<1.0:		# rotate right
            client.send(json.dumps({'motion':[tran,rot+0.2]}))		# ALL STOP
            message = client.recv()
        if event == 260 and rot>-1.0:		# rotate left
            client.send(json.dumps({'motion':[tran,rot-0.2]}))		# ALL STOP
            message = client.recv()

        if event == ord('r'): 			# reset all
            client.send(json.dumps({'motion':[0.0,0.0]}))		# ALL STOP
            message = client.recv()
            client.send(json.dumps({'pose':[0.0,0.0,0.0]}))		# ALL STOP
            message = client.recv()
        time.sleep(0.05)

HOST = ''
PORT = 9888

client = messaging.Client(HOST, PORT)

c.wrapper(main, client)

print
print "exited"
