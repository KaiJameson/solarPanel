import random
import math


class SolarLayout:
  def __init__(self, layout=None):
    self.maxDistance = 120
    self.panelCount = 80
    self.score = 0
    #starting from scratch
    if layout is None:
      self.generateLayout()
    #being given a string to make into a layout
    else:
      self.convertFromString(layout)
    self.setPoints()


  def generateLayout(self):
    lst = []
    #generate all polar coordinates of solar trackers
    for i in range(self.panelCount):
      lst.append(self.generatePanel())
    self.layout = lst


  def generatePanel(self):
    #pick a random polar coordinate that is within self.maxDistance of the 0,0
    angle = math.radians(random.randint(0,360))
    distance = random.randint(0,self.maxDistance)
    return (angle,distance)


  def __str__(self):
    return self.makeString(self.layout)

  #create a layout from string of polar coordinates
  def convertFromString(self, layoutString):
    panels = layoutString.strip().split(",")
    lst = []
    for panel in panels:
      parts = panel.split("|")
      lst.append((float(parts[0]), int(parts[1])))
    self.layout = lst


  def mutatePanel(self, panel):
    #convert the panel from polar coordinate to x,y coordinate
    startingPoint = [panel[1]*math.cos(panel[0]),panel[1]*math.sin(panel[0])]
    #list of possible angles directions to move in
    angles = [math.radians(i* 30) for i in range(12)]
    #how far away from starting location to move
    distance = random.randint(2,4)
    #shuffle to get a random angle at the front
    random.shuffle(angles)
    angle = angles.pop()
    movement = [distance*math.cos(angle), distance*math.sin(angle)] 
    #new location
    point = [startingPoint[0]+movement[0], startingPoint[1]+movement[1]]
    #while the location is outside the bounds
    while self.dist(point) > self.maxDistance:
      #if all angles have been exhausted, return an entirely new tracker in random location
      if (len(angles) == 0):
        print("distance of " + str(self.dist(point)))
        return self.generatePanel()
      #get a new angle to check
      angle = angles.pop()
      movement = [distance*math.cos(angle), distance*math.sin(angle)] 
      point = [startingPoint[0]+movement[0], startingPoint[1]+movement[1]]
    #convert the point back to polar coordinate
    return self.getTuple(point)


  #standard distance formula
  def dist(self, point):
    return ((point[0]**2)+(point[1]**2))**.5


  def getTuple(self, point):
    angle = math.atan(point[1]/point[0])
    if point[0] < 0:
      angle += math.pi
    return (angle, self.dist(point))

  #convert list of coordinates from polar to x,y
  def setPoints(self):
    self.points = [(d*math.cos(angle), d*math.sin(angle), 0) for (angle, d) in self.layout]

  def getPoints(self):
    return self.points

  #set the score of this layout to be used for comparisons
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


  #using the add operator for crossover in the genetic algorithm
  def __add__(self,other):
    #generate a random start and end index 
    start = random.randint(0,self.panelCount-1)
    end = random.randint(0,self.panelCount-1)
    #make sure end and start are different
    while start == end:
      end = random.randint(0,self.panelCount-1)
    #make sure that start is less than end
    if start > end:
      temp = start 
      start = end
      end = temp
    #child layout starts as parent 1 (self)
    childLayout = self.layout[:]
    secondParentLayout = other.getLayout()
    #for each index in the range, change that index in child to be the same as the second parent
    for i in range(start,end+1):
      childLayout[i] = secondParentLayout[i]
    #create a new layout for the child
    return SolarLayout(self.makeString(childLayout))
    
  def mutate(self):
    #mutate 20% of the solar trackers
    mutateCt = self.panelCount // 5
    mutated = []
    for i in range(mutateCt):
      #randomly decide which trackers to mutate
      mutateIdx = random.randint(0,self.panelCount-1)
      #making sure not to mutate the same trackers multiple times in one generation
      while mutateIdx in mutated:
        mutateIdx = random.randint(0,self.panelCount-1)
      self.layout[mutateIdx] = self.mutatePanel(self.layout[mutateIdx])
      mutated.append(mutateIdx)
    self.setPoints()
    

