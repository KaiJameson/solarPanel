import random
import math
class SolarLayout:
  def __init__(self, layout=None):
    self.maxDistance = 120
    self.panelCount = 80
    self.score = 0
    if layout is None:
      self.generateLayout()
    else:
      self.convertFromString(layout)
    self.setPoints()

  def generateLayout(self):
    lst = []
    for i in range(self.panelCount):
      lst.append(self.generatePanel())
    self.layout = lst
  def generatePanel(self):
    angle = math.radians(random.randint(0,360))
    distance = random.randint(0,self.maxDistance)
    return (angle,distance)

  def __str__(self):
    return self.makeString(self.layout)

  def convertFromString(self, layoutString):
    panels = layoutString.strip().split(",")
    lst = []
    for panel in panels:
      parts = panel.split("|")
      lst.append((float(parts[0]), int(parts[1])))
    self.layout = lst

  def setPoints(self):
    self.points = [(d*math.cos(angle), d*math.sin(angle), 0) for (angle, d) in self.layout]

  def getPoints(self):
    return self.points

  def setScore(self, score):
    self.score = score
  
  def getScore(self):
    return self.score

  def getLayout(self):
    return self.layout

  def __gt__(self, other):
    if self.getScore() > other.getScore():
      return True
    return False

  def __lt__(self,other):
    if self.getScore() < other.getScore():
      return True
    return False

  def makeString(self, layout):
    layoutString = ""
    for i in range(len(layout)-1):
      layoutString += "%.4f|%d," % layout[i]
    layoutString += "%.4f|%d" % layout[len(layout)-1]
    return layoutString

  def __add__(self,other):
    start = random.randint(0,self.panelCount-1)
    end = random.randint(0,self.panelCount-1)
    while start == end:
      end = random.randint(0,self.panelCount-1)
    if start > end:
      temp = start 
      start = end
      end = temp
    childLayout = self.layout[:]
    secondParentLayout = other.getLayout()
    for i in range(start,end+1):
      childLayout[i] = secondParentLayout[i]
    return SolarLayout(self.makeString(childLayout))
    
  def mutate(self):
    mutateCt = self.panelCount // 5
    mutated = []
    for i in range(mutateCt):
      mutateIdx = random.randint(0,self.panelCount-1)
      while mutateIdx in mutated:
        mutateIdx = random.randint(0,self.panelCount-1)
      self.layout[mutateIdx] = self.generatePanel()
      mutated.append(mutateIdx)
    self.setPoints()
    

