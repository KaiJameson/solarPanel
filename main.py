import CityVisualizer
import SolarLayout 
import os
import random



#check to see if a current  generation already exists
#if true: start by loading that generation
#generations will have 2 parents saved

# visualizer = CityVisualizer.CityVisualizer("Omaha")
# layout = SolarLayout.SolarLayout()
# visualizer.oneDaySimulation(layout.getPoints(), sampleTime=5)
# layout.setScore(visualizer.process())
city = "Omaha"

generationStorage = "currentGeneration.txt"
bestOfStorage = "bestOf.csv"
def checkExistingGeneration():
  return os.path.exists(generationStorage)

def loadGeneration():
  layouts = []
  if checkExistingGeneration():
    f = open(generationStorage, "r")
    for line in f:
      layouts.append(SolarLayout.SolarLayout(line.strip()))
    f.close()
  else:
    for i in range(2):
      layouts.append(SolarLayout.SolarLayout())
  return layouts

def generationNum():
  if checkExistingGeneration():
    #figure it out
    f = open(bestOfStorage, "r")
    lines = f.readlines()
    f.close()
    return len(lines)
  else:
    return 0
generationSize = 2
currentGeneration = loadGeneration()
generationCt = generationNum()
while True:
  print(f"Starting generation {generationCt}")
  #create 2 children
  for i in range(generationSize):
    currentGeneration.append(currentGeneration[0]+currentGeneration[1])
  #randomly mutate up to half the population of this generation
  for i in range(random.randint(0,len(currentGeneration)//2)):
    toMutate = random.randint(0,len(currentGeneration)-1)
    currentGeneration[toMutate].mutate()
  for layout in currentGeneration:
    visualizer = CityVisualizer.CityVisualizer(city)
    visualizer.oneDaySimulation(layout.getPoints(), sampleTime=30)
    layout.setScore(visualizer.process())
  print("sorting")
  currentGeneration.sort()
  
  nextGeneration = []
  for i in range(generationSize):
    nextGeneration.append(currentGeneration[len(currentGeneration)-1-i])

# visualizer = CityVisualizer.CityVisualizer("Omaha")
# layout = SolarLayout.SolarLayout()
# visualizer.oneDaySimulation(layout.getPoints(), sampleTime=5)
# layout.setScore(visualizer.process())

  print("Saving the current generation")
  f = open(generationStorage, "w")
  for layout in nextGeneration:
    f.write(str(layout)+"\n")
  f.close()
  print("Saving best of")
  bestOf = open(bestOfStorage, "a")
  bestOf.write(str(nextGeneration[0])+","+str(nextGeneration[0].getScore())+"\n")
  bestOf.close()
  print("Done saving info")
  currentGeneration = nextGeneration
  generationCt += 1


