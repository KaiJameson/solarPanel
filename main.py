import CityVisualizer
import SolarLayout 
import os
import random
import json




city = "Omaha"

generationStorage = "currentGeneration.txt"
bestOfStorage = "bestOf.csv"
jsonScores = "scores.json"
def checkExistingGeneration():
  return os.path.exists(generationStorage)

def loadGeneration():
  global generationSize
  layouts = []
  if checkExistingGeneration():
    f = open(generationStorage, "r")
    for line in f:
      layouts.append(SolarLayout.SolarLayout(line.strip()))
    f.close()
  else:
    for i in range(generationSize):
      layouts.append(SolarLayout.SolarLayout())
  return layouts

def generationNum():
  if checkExistingGeneration():
    #figure it out
    f = open(bestOfStorage, "r")
    lines = f.readlines()
    f.close()
    return len(lines)+1
  else:
    return 0


generationSize = 10
#check to see if a current  generation already exists
#if true: start by loading that generation
currentGeneration = loadGeneration()
generationCt = generationNum()

def load_scores():
  if os.path.exists(jsonScores):
    f = open(jsonScores)
    scores = json.load(f)
    f.close()
    return scores
  else:
    return {}

#load previously calculated scores to avoid extra work in training
scores = load_scores()

def save_scores(scores):
  f = open(jsonScores, "w")
  json.dump(scores,f,ensure_ascii=False,indent=2)
  f.close()


while True:
  print(f"Starting generation {generationCt}")
  #create generationSize children
  for i in range(generationSize-1):
    currentGeneration.append(currentGeneration[i]+currentGeneration[i+1])
  currentGeneration.append(currentGeneration[0]+currentGeneration[len(currentGeneration)-1])
  #randomly mutate up to half the population of this generation
  for i in range(random.randint(0,len(currentGeneration)//2)):
    toMutate = random.randint(0,len(currentGeneration)-1)
    currentGeneration[toMutate].mutate()
  #for every layout, calculate their fitness score
  for layout in currentGeneration:
    #if this layouts score has laready been calculated, avoid calculating it again
    if str(layout) in scores.keys():
      layout.setScore(scores[str(layout)])
    else:
      visualizer = CityVisualizer.CityVisualizer(city)
      visualizer.generalSimulation(layout.getPoints(), 60)
      layout.setScore(visualizer.process())
      #save the fitness value of this layout for possible future use
      scores[str(layout)] = layout.getScore()
  print("sorting")
  #sort to find the best of each generation
  currentGeneration.sort()
  nextGeneration = []
  #the best of each generation will be towards the end
  for i in range(generationSize):
    nextGeneration.append(currentGeneration[len(currentGeneration)-1-i])

  print("Saving the current generation")
  f = open(generationStorage, "w")
  for layout in nextGeneration:
    f.write(str(layout)+"\n")
  f.close()
  print("Saving best of")
  bestOf = open(bestOfStorage, "a")
  bestOf.write(str(nextGeneration[0])+"_"+str(nextGeneration[0].getScore())+"\n")
  bestOf.close()
  print("saving scores")
  save_scores(scores)
  print("Done saving info")
  currentGeneration = nextGeneration
  generationCt += 1


