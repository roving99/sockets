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

sonarMap = None

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
    y=16
    x=1
    for i in range(len(coordSystem)):
        screen.addstr(y+i,x,coordSystem[i])
    # raw data
    x = 1
    y = 26
    for key in data.keys():
        d = data[key]
        screen.addstr(y,x, str(key).rjust(10)+"  "+str(data[key]).ljust(40))
        y += 1
#    screen.addstr(y,x,str(sonarMap))

def updateMap(screen, map):
    width = 50
    height = 30
    range_ = 100 # cm
    for i in range(height):
        screen.addstr(i, 60, " "*width)
    if sonarMap:
        for hit in sonarMap:
            y = int(hit[1]*((height/2.)/range_))
            x = int(hit[0]*((width/2.)/range_))
            if abs(y)<(height/2) and abs(x)<(width/2):
                screen.addstr(int((height/2) - y), int(60 + (width/2) - x), "+")

def make_json_rpc(method, params, id):
    return json.dumps({"method":method, "params":params, "id":id})

def main(screen, client):
    global sonarMap
    id = 1000
    screen.addstr("MD25 robot control 0.2\n\n") 
    screen.nodelay(1)
    while True: 
        client.send(make_json_rpc("get", "all", id))
        message = client.recv()
        data = json.loads(message)
        world = data["result"]
    
        update(screen, world)
        updateMap(screen, sonarMap)
        event = screen.getch() 
        screen.addstr(15,0,str(event)+"   ")

        if event == ord("q"): break 

        tran = world['motion'][0]
        rot  = world['motion'][1]
        if event == 32:
            client.send(make_json_rpc("stop", None, id))
            message = client.recv()

        if event == 259 and tran<1.0:		# forward
            client.send(make_json_rpc("move", [tran+0.2,rot], id))
            message = client.recv()
        if event == 258 and tran>-1.0:		# reverse
            client.send(make_json_rpc("move", [tran-0.2,rot], id))
            message = client.recv()
        if event == 261 and rot<1.0:		# rotate right
            client.send(make_json_rpc("move", [tran,rot+0.2], id))
            message = client.recv()
        if event == 260 and rot>-1.0:		# rotate left
            client.send(make_json_rpc("move", [tran,rot-0.2], id))
            message = client.recv()

        if event == ord('m'): 			# reset map
            client.send(make_json_rpc("get", "sonarMapRect", id))
            message = client.recv()
            sonarMap = json.loads(message)['result']
        if event == ord('M'): 			# reset map
            client.send(make_json_rpc("resetMap", None, id))
            message = client.recv()

        if event == ord('r'): 			# reset all
            client.send(make_json_rpc("reset", None, id))
            message = client.recv()
        time.sleep(0.05)

HOST = ''
PORT = 9888


client = messaging.Client(HOST, PORT)

c.wrapper(main, client)

print
print "exited"
