import random
import math
class SolarLayout:
  def __init__(self, layout=None):
    self.maxDistance = 120
    self.panels = 80
    if layout is None:
      self.generateLayout()
    # else:

  def generateLayout(self):
    lst = []
    for i in range(self.panels):
      lst.append(self.generatePanel())

  def generatePanel(self):
    angle = math.radians(random.randint(0,360))
    distance = random.randint(0,self.maxDistance)
    return (angle,distance)











