import Tkinter
import math
import zmq

import messaging

def clamp(n, minn, maxn):
        return max(min(maxn, n), minn)

class Joystick(Tkinter.Toplevel):

   def __init__(self, parent = None, client=None, onQuit=None):
      Tkinter.Toplevel.__init__(self, parent)
      self.client = client
      self.debug = 0
      self.hasZ = 0
      self.wm_title('Joystick')
      self.protocol('WM_DELETE_WINDOW',onQuit)
      self.springBack = 0
      self.mBar = Tkinter.Frame(self, relief=Tkinter.RAISED, borderwidth=2)
      self.mBar.pack(fill=Tkinter.X)
      self.goButtons = {}
      self.menuButtons = {}
      self.robot = []
      self.heightScaleValue = 0
      self.variableBearing = Tkinter.StringVar()
      self.variableBearing.set(360)
      
      menu = [('Options',[['Toggle spring-back to center', self.toggleSpringBack],
                          ]),
              ]
      for entry in menu:
         self.mBar.tk_menuBar(self.makeMenu(self.mBar, entry[0], entry[1]))
      self.mainFrame = Tkinter.Frame(self)
      self.frame = Tkinter.Frame(self.mainFrame)
      label = Tkinter.Label(self.frame, text = "Forward")
      label.pack(side = "top")

      self.fieldBearing = Tkinter.Label(self.frame, textvariable=self.variableBearing)
      self.fieldBearing.pack(side = "top")
      
      label = Tkinter.Label(self.frame, text = "Reverse")
      label.pack(side = "bottom")
      label = Tkinter.Label(self.frame, text = "Turn\nLeft")
      label.pack(side = "left")
      label = Tkinter.Label(self.frame, text = "Turn\nRight")
      label.pack(side = "right")
      self.canvas = Tkinter.Canvas(self.frame,
                                   width = 320,
                                   height = 320,
                                   bg = 'white')
      self.initHandlers()
      self.canvas.pack(side=Tkinter.BOTTOM)
      self.circle_dim = (60, 60, 260, 260) #x0, y0, x1, y1
      self.circle = self.canvas.create_oval(self.circle_dim, fill = 'white')
      self.canvas.create_oval(155, 155, 165, 165, fill='black')
      self.frame.pack(side='left')
      self.goButtons["Stop"] = Tkinter.Button(self,text="Stop",command=self.stop)
      self.goButtons["Stop"].pack(side=Tkinter.BOTTOM,padx=2,pady=2,fill=Tkinter.X, expand = "yes", anchor="s")
      self.mainFrame.pack()
      self.translate = 0.0
      self.rotate = 0.0
      self.threshold = 0.10
      self.update()

   def toggleSpringBack(self):
      self.springBack = not self.springBack
      
   def makeMenu(self, bar, name, commands):
      """ Assumes self.menuButtons exists """
      menu = Tkinter.Menubutton(bar,text=name,underline=0)
      self.menuButtons[name] = menu
      menu.pack(side=Tkinter.LEFT,padx="2m")
      menu.filemenu = Tkinter.Menu(menu)
      for cmd in commands:
         if cmd:
            menu.filemenu.add_command(label=cmd[0],command=cmd[1])
         else:
            menu.filemenu.add_separator()
      menu['menu'] = menu.filemenu
      return menu

   def setHeightScale(self, event = None):
      self.heightScaleValue = self.heightScale.get()
      if self.hasZ:
         self.move(self.translate, self.rotate, self.heightScaleValue)
      else:
         self.move(self.translate, self.rotate)

   def initHandlers(self):
      self.canvas.bind("<ButtonRelease-1>", self.canvas_clicked_up)
      self.canvas.bind("<Button-1>", self.canvas_clicked_down)
      self.canvas.bind("<B1-Motion>", self.canvas_moved)

   def getValue(self, event = None):
      return self.translate, self.rotate

   def _move(self, translate, rotate):
      self.translate = translate
      self.rotate = rotate
      if self.hasZ:
         self.move(self.translate, self.rotate, self.heightScaleValue)
      else:
         self.move(self.translate, self.rotate)

   def move(self, x, y, z = 0):
      if self.debug:
         print x, y, z
      self.client.send('MOVE', [clamp(self.translate,-1.0, 1.0),clamp(0.0-self.rotate,-1.0, 1.0)])
      self.client.recv()
      
   def canvas_clicked_up(self, event):
      if not self.springBack:
         self.canvas.delete("lines")
         self._move(0.0, 0.0)
#         print "s",
         
   def drawArrows(self, x, y, trans, rotate):
      if trans == 0:
         self.canvas.create_line(160, 160, 160, y, width=3, fill="blue", tag="lines")
      else:
         self.canvas.create_line(160, 160, 160, y, width=3, fill="blue", tag="lines", arrowshape = (10, 10, 3), arrow = "last")
      if rotate == 0:
         self.canvas.create_line(160, 160, x, 160, width=3, fill="green", tag="lines")
      else:
         self.canvas.create_line(160, 160, x, 160, width=3, fill="green", tag="lines", arrowshape = (10, 10, 3), arrow = "last")
      self.update()

   def update(self):
      self.robot = self.client.all()
      angle = float(self.robot['pose'][2])
      self.variableBearing.set(angle)
      self.canvas.delete("arcs")
      self.drawSonar(90,20,float(self.robot['sonar'][0]))
      self.drawSonar(180,20,float(self.robot['sonar'][1]))
      self.canvas.delete("arrows")
      self.drawCompass(math.radians(angle))
      self.canvas.after(100,self.update)
      
   def drawCompass(self, angle):   # delta in rads
      angle = (angle/(2*math.pi))*360
      self.canvas.create_line(160-130*math.sin(angle),160-130*math.cos(angle), 160-150*math.sin(angle), 160-150*math.cos(angle), fill="red", arrowshape = (20,20,20), arrow = "last", tag="arrows")

   def drawSonar(self,angle,delta,length):
      if length>160:
         length = 160
      xy = 160-length, 160-length, 160+length, 160+length         
      self.canvas.create_arc(xy, start=angle-delta/2, extent=delta, fill="blue", tag="arcs")

   def canvas_clicked_down(self, event):
      if self.in_circle(event.x, event.y):
         self.canvas.delete("lines")
         trans, rotate = self.calc_tr(event.x, event.y)
         self.drawArrows(event.x, event.y, trans, rotate)
         self._move(trans, rotate)

   def canvas_moved(self, event):
      if self.in_circle(event.x, event.y):
         self.canvas.delete("lines")
         trans, rotate = self.calc_tr(event.x, event.y)
         self.drawArrows(event.x, event.y, trans, rotate)         
         self._move(trans, rotate)

   def stop(self, event = None):
      if self.hasZ:
         self.heightScale.set(0)
      self.canvas.delete("lines")
      self._move(0.0, 0.0)

   def in_circle(self, x, y):
      return 1

   def calc_tr(self, x, y):
      #right is negative
      center = ((self.circle_dim[2] + self.circle_dim[0])/2,
                (self.circle_dim[3] + self.circle_dim[1])/2)
      rot = float(center[0] - x) / float(center[0] - self.circle_dim[0])
      trans = float(center[1] - y) / float(center[1] - self.circle_dim[1])
      if abs(rot) < self.threshold:
         rot = 0.0
      if abs(trans) < self.threshold:
         trans = 0.0
      return (trans, rot)

def onQuit():
   client.kill()
   app.quit()

if __name__ == '__main__':
#   port = "5558"
   port = messaging.ports['md25_server']

#   publisher = messaging.Publisher(port, ['move'])
   client = messaging.Client(port)

   app = Tkinter.Tk()
   app.withdraw()
   joystick = Joystick(parent = app, client=client, onQuit=onQuit)
   app.mainloop()

