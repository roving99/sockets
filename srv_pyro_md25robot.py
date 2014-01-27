#!/usr/bin/python
# Pyro server - gets data from md25 robot and serves as a pyro RPC

import random
import sys
import time
import math
import copy
import json

#import messaging
import md25

import Pyro.core
import Pyro.naming


class Movement(Pyro.core.ObjBase):

    def _setup(self, robot):
        self.robot = robot

    def __init__(self, robot):
        Pyro.core.ObjBase.__init__(self)
        self._setup(robot)

    def move(self, t,r):        
        self.robot.move(t, r)

    def stop(self):        
        self.robot.move(0.0,0.0)

    def forward(self, move_time):
        self.robot.move(0.4,0.0)

    def backward(self, move_time):
        self.robot.move(-0.4,0.0)

    def left(self, move_time):
        self.robot.move(0.0,0.5)
   
    def right(self, move_time):
        self.robot.move(0.0,-0.5)

    def all(self):
        return self.robot.get('all', False)

m=md25.Md25()


if __name__ == "__main__":
    # Create a Pyro server and register our module with it
    Pyro.core.initServer()
    ns = Pyro.naming.NameServerLocator().getNS()
    daemon = Pyro.core.Daemon()
    daemon.useNameServer(ns)
    uri = daemon.connect(Movement(m),"robotmovement")
    daemon.requestLoop()
