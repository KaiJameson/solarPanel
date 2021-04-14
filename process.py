import os
import subprocess
import glob
import time 
from PIL import Image
from numpy import asarray
import sys
import datetime

#step 1) Add "C:\Program Files\POV-Ray\v3.7\bin" to your environment variables path. (Hopefully the target is the same for your computer)
#step 2) open up povray.
#step 3) go to "options", and disable "keep single instance"
#step 4) run this code! it should work!
start = datetime.datetime.now()
print(start)
# subprocess.call("cd", shell=True)
os.chdir(os.path.abspath(os.path.expanduser('reflector/Wilmington'))) #navigate to the target folder with the pov files.
#Depending on where you put this file, you might need to change
my_env = os.environ.copy()

povFiles = glob.glob("*.pov")
print(len(povFiles))
for povFile in povFiles:
  # print(povFile)
  subprocess.run(["pvengine" , "-d",povFile])
  # subprocess.Popen(f"start pvengine {povFile} -d /exit", shell=False)
done = False 
pngFiles = []
while not done:
  pngFiles = glob.glob("*.png")
  if len(pngFiles) == len(povFiles):
    done = True
  time.sleep(1)
print("done with png processing")
sunPixels = 0
for pngFile in pngFiles:
  image = Image.open(pngFile)
  data = asarray(image)
  totalPixels = len(data)*len(data[0])
  for i in range(len(data)):
    for j in range(len(data[0])):
      white = True
      for k in range(3):
        if data[i][j][k] < 255:
          white = False 
      if white:
        sunPixels += 1

print("sunscore is " + str(sunPixels))

end = datetime.datetime.now()
duration = end-start 
print(duration)

