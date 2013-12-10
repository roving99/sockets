import math

class Pose():
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta

    def add(self,pose):
        self.x += pose.x
        self.y += pose.y
        self.theta += pose.theta
        self.theta = self.theta%(math.pi*2)
        return self

    def asText(self):
        return "(%s, %s, %s)" % (str(self.x), str(self.y), str(self.theta))

if __name__=="__main__":
    p = Pose(0,0,0)
    next = Pose(100,100,0)
    sum = p.add(next)
    print p.asText(), "+", next.asText(), "=", sum.asText()

