import random
import math
class SolarLayout:
  def __init__(self, layout=None):
    self.maxDistance = 120
    self.panels = 80
    self.score = 0
    if layout is None:
      self.generateLayout()
    else:
      self.convertFromString(layout)

  def generateLayout(self):
    lst = []
    for i in range(self.panels):
      lst.append(self.generatePanel())
    self.layout = lst
  def generatePanel(self):
    angle = math.radians(random.randint(0,360))
    distance = random.randint(0,self.maxDistance)
    return (angle,distance)

  def __str__(self):
    layout = ""
    for i in range(len(self.layout)-1):
      layout += "%.4f|%d," % self.layout[i]
    layout += "%.4f|%d" % self.layout[len(self.layout)-1]
    return layout

  def convertFromString(self, layoutString):
    panels = layoutString.strip().split(",")
    lst = []
    for panel in panels:
      parts = panel.split("|")
      lst.append(float(parts[0]), int(parts[1]))
    self.layout = lst

  def setScore(self, score):
    self.score = score
  
  def getScore(self):
    return self.score

  def __gt__(self, other):
    if self.getScore() > other.getScore():
      return True
    return False

  def __lt__(self,other):
    if self.getScore() < other.getScore():
      return True
    return False

