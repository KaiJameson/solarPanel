import CityVisualizer
import SolarLayout 
import os

generation = 27



city = "Omaha"
bestOfStorage = "bestOf.csv"

scores = []
layouts = []

f = open(bestOfStorage, "r")
for line in f:
  parts = line.strip().split("_")
  layouts.append(parts[0])
  scores.append(int(parts[1]))
f.close()


visualizer = CityVisualizer.CityVisualizer(city)
layout = SolarLayout.SolarLayout(layouts[generation])
visualizer.oneDaySimulation(layout.getPoints(), sampleTime=5)
visualizer.process()




