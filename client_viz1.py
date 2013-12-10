# File: hello6.py

from Tkinter import *
import socket
import thread
import json
import messaging
import maps
import time
import math

class App:

    def __init__(self, master, text='default', function=None):

        frame = Frame(master)
        frame.pack()

        self.button = Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.button.pack(side=LEFT)

        if function==None:
            self.hi_there = Button(frame, text=text, command=self.say_hi)
        else:
            self.hi_there = Button(frame, text=text, command=function)
        self.hi_there.pack(side=LEFT)

    def say_hi(self):
        print "hi there, everyone!"

class InfoFrame:

    def __init__(self, master, world):
        self.master = master
        self.world = world
        self.labelMap = {}
        
        self.frame = Frame(self.master, borderwidth=2, relief=RAISED)
        self.frame.pack(fill = X, side=TOP)
        Label(self.frame, text = 'Information', fg='white', bg='black').pack(fill=X, side=TOP)
        for info in world.keys():
            littleFrame = Frame(self.frame)
            littleFrame.pack(fill=X, side=TOP)
            Label(littleFrame, text = str(info), fg='red', width=10).pack(side=LEFT)
            list = []
            for value in world[info]:
                label =Label(littleFrame, text = str(value), fg='blue')
                label.pack(side=LEFT)
                list.append(label)
            self.labelMap[info] = list

class SonarFrame:

    def __init__(self, master, world):
        self.master = master
        self.world = world
        self.labelMap = {}
        self.gaussians = [ maps.Gaussian(world['sonar'][0],200),
                           maps.Gaussian(world['sonar'][1],200),
                           maps.Gaussian(world['sonar'][2],200),
                           maps.Gaussian(world['sonar'][3],200),
                         ]
        
        root.bind_all('<Key>', self.key)

        self.frame = Frame(self.master, borderwidth=2, relief=RAISED)                # .pack returns 0!!
        self.frame.pack(fill = X, side=TOP)
        Label(self.frame, text = ' Sonar', fg='white', bg='black').pack(fill=X, side=TOP)
        self.canvas = Canvas(self.frame, width=400, height=400, bg='gray')
        self.canvas.pack()
        self.draw()
        self.update_labels()

    def draw(self):
        dth = math.pi/64
        x = 200
        y = 200
        for i in range(0,64):
            th = maps.slotToTheta(i)+math.pi
            self.canvas.create_line(x,y,x+150.*math.sin(th+dth), y+150.*math.cos(th+dth), fill="white", tag="axis")
            self.canvas.create_line(x,y,x+150.*math.sin(th-dth), y+150.*math.cos(th-dth), fill="white", tag="axis")
            for r in [50,100,150]:
                self.canvas.create_line(x+r*math.sin(th-dth), y+r*math.cos(th-dth), x+r*math.sin(th+dth), y+r*math.cos(th+dth), fill="white", tag="axis")
        """
        for i in [0,1,2,3]:
            g = self.gaussians[i]
            self.canvas.create_line(50, 150+i*120, 350, 150+i*120, fill="white", tag="axis")
            self.canvas.create_line(50, 150+i*120, 50, 50+i*120, fill="white", tag="axis")
            for x in range(5,300,1):
                self.canvas.create_line(50+x-1, 150+i*120-(400*g.fn(x-1)), 50+x, 150+i*120-(400*g.fn(x)), fill="red", tag="plot")
        """

    def update(self):
        dth = (math.pi/64)*.9
        x = 200
        y = 200
        self.canvas.delete("plot")
        for i in range(0,64):
            th = maps.slotToTheta(i)+math.pi
            r = sonarWorld[i][0]/2.
            v = sonarWorld[i][1]/2.
            self.canvas.create_line(x+r*math.sin(th-dth), y+r*math.cos(th-dth),
                                    x+r*math.sin(th+dth), y+r*math.cos(th+dth), fill="blue", tag="plot")
            self.canvas.create_line(x+(r-v)*math.sin(th), y+(r-v)*math.cos(th),
                                    x+(r+v)*math.sin(th), y+(r+v)*math.cos(th), fill="blue", tag="plot")
            """
            self.canvas.create_arc(x-r, y-r, x+r, y+r,
                                   start=math.degrees(th-dth), extent=math.degrees(2.*dth),
                                   fill="blue", tag="plot")
            """
            
        """
        self.canvas.delete("axis")
        self.canvas.delete("plot")
        for i in [0,1,2,3]:
            g = self.gaussians[i]
            self.canvas.create_line(50, 150+i*120, 350, 150+i*120, fill="white", tag="axis")
            self.canvas.create_line(50, 150+i*120, 50, 50+i*120, fill="white", tag="axis")
            for x in range(5,300,2):
                self.canvas.create_line(50+x-2, 150+i*120-(400*g.fn(x-2)), 50+x, 150+i*120-(400*g.fn(x)), fill="red", tag="plot")
        """
    def update_labels(self):
        """
        for i in [0,1,2,3]:
            self.gaussians[i].update(world['sonar'][i], 5)
        """
        self.update()                
        self.frame.after(500, self.update_labels)  # 1000ms
    
    def key(self,event):
        pass

class SensorFrame:

    def __init__(self, master, world):
        self.master = master
        self.world = world
        self.labelMap = {}
        
        root.bind_all('<Key>', self.key)

        self.frame = Frame(self.master, borderwidth=2, relief=RAISED)                # .pack returns 0!!
        self.frame.pack(fill = X, side=TOP)
        Label(self.frame, text = ' Sensors', fg='white', bg='black').pack(fill=X, side=TOP)
        for sensor in world.keys():
            littleFrame = Frame(self.frame)
            littleFrame.pack(fill=X, side=TOP)
            Label(littleFrame, text = str(sensor), fg='red', width=10).pack(side=LEFT)
            list = []
            for value in world[sensor]:
                label =Label(littleFrame, text = str(value), fg='blue', width=5)
                label.pack(side=LEFT)
                list.append(label)
            self.labelMap[sensor] = list
            
        self.update_labels()

    def update_labels(self):
        for sensor in self.labelMap.keys():
            for i in range(len(self.labelMap[sensor])):
#                self.labelMap[sensor][i].config(text=self.world[sensor][i])
                self.labelMap[sensor][i].config(text=world[sensor][i])
                
        self.frame.after(500, self.update_labels)  # 1000ms

    def key(self,event):
        if event.keysym == 'Escape':
            root.destroy()
        if event.char == event.keysym:
            # normal number and letter characters
            print( 'Normal Key %r' % event.char )
        elif len(event.char) == 1:
            # charcters like []/.,><#$ also Return and ctrl/key
            print( 'Punctuation Key %r (%r)' % (event.keysym, event.char) )
            k = event.keysym 
            if k=='space':
                pass #self.robot.stop()
        else:
            # f1 to f12, shift keys, caps lock, Home, End, Delete ...
            print( 'Special Key %r' % event.keysym )
            k = event.keysym 
            if k=='Up':
                pass #self.robot.translate(0.5)
            if k=='Down':
                pass #self.robot.translate(-0.5)
            if k=='Left':
                pass #self.robot.rotate(-0.5)
            if k=='Right':
                pass #self.robot.rotate(0.5)

class MapFrame:

    def __init__(self, master, world, map, x=250, y=250, scale=0.5):
        self.master = master
        self.world = world
        self.map = map
        self.scale = scale   # 1px = 2cm.
        self.x = x
        self.y = y
        self.labelMap = {}
        
#        self.frame = Frame(self.master, borderwidth=2, relief=RAISED)                # .pack returns 0!!
        self.frame = Toplevel()                # .pack returns 0!!
#        self.frame.pack(fill = X, side=TOP)
#        self.frame.pack()
        Label(self.frame, text = 'Map', fg='white', bg='black').pack(fill=X, side=TOP)
        canvas = Canvas(self.frame, width=x, height=y, bg='gray')
        canvas.pack()
    
        self.update_labels()

    def update_labels(self):
        points = self.map.listRect()
        for sensor in self.labelMap.keys():
            for i in range(len(self.labelMap[sensor])):
                self.labelMap[sensor][i].config(text=world[sensor][i])
                
        self.frame.after(500, self.update_labels)  # 1000ms


def say(text):
    print text

HOST = ''
PORT = 9888

PORT_MAPPER = 9889

world = [{},]

sonarWorld = []
for i in range(0,64):
    sonarWorld.append([i*4,i])  # pretty spiral!

def clientThread(s):
    global world
    while True:
        s.send("[]")
        data = s.recv(1024)
        if not data:
            break
        try:
            j = json.loads(str(data))
        except:
            print 'bad data :',data
        else:
            world = j[0]
#            print world

        time.sleep(0.5)

    print addr[0],':',addr[1], 'disconnected'
    conn.close()


def clientThreadSonar(s):
    global sonarWorld
    while True:
        s.send("[]")
        data = s.recv(4*1024)
        if not data:
            break
        try:
            j = json.loads(str(data))
        except:
            print 'bad data :',data
        else:
            sonarWorld = j[0]
#            print world

        time.sleep(0.5)

    print addr[0],':',addr[1], 'disconnected'
    conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'created socket'

try:
    s.connect((HOST, PORT))
    ss.connect((HOST, PORT_MAPPER))
except socket.error, msg:
    print 'FAILED to connect. Error :',msg[0], 'Message', msg[1]
    sys.exit()

print 'Connected to', HOST,':', PORT
print 'Connected to', HOST,':', PORT_MAPPER
print 'starting threaded client.'

thread.start_new_thread(clientThread, (s,))
thread.start_new_thread(clientThreadSonar, (ss,))

root = Tk()
#localMap = maps.Map()
#largeMap = maps.Map()

app2 = App(root, "this", lambda: say("this"))

#frame_sensor = SensorFrame(root, world)
frame_sonar = SonarFrame(root, world)
#frame_info= InfoFrame(root, world)
#frame_map = MapFrame(root, world, localMap)
#frame_bigMap = MapFrame(root, world, largeMap, x=500, y=500, scale=0.25)

root.mainloop()

