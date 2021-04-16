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
pngFiles = []
threshhold = 10
idx = 0
while idx < len(povFiles):
  if idx < len(pngFiles) + threshhold:
    subprocess.Popen(f"start pvengine {povFiles[idx]} -d Grayscale_Output=true /exit", shell=True)
    idx += 1
  else:
    pngFiles = glob.glob("*.png")
    time.sleep(.25)
done = False 
while not done:
  pngFiles = glob.glob("*.png")
  if len(pngFiles) == len(povFiles):
    done = True
print("done with png processing")
sunPixels = 0
for pngFile in pngFiles:
  image = Image.open(pngFile)
  data = asarray(image)
  totalPixels = len(data)*len(data[0])
  for i in range(len(data)):
    for j in range(len(data[0])):
      # white = True
      if data[i][j] == 65535:
        sunPixels += 1
      # for k in range(3):
      #   if data[i][j][k] < 255:
      #     white = False 
      #     break
      # if white:
        # sunPixels += 1

print("sunscore is " + str(sunPixels))

end = datetime.datetime.now()
duration = end-start 
print(duration)

