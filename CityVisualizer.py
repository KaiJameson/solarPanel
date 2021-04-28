import numpy as np
import math
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import matplotlib.pyplot as plt
import os.path
import operator
from dateutil.relativedelta import relativedelta
from numpy import asarray
from astral import geocoder
from astral import location
import astral
import sys
import os
import subprocess
import glob
import time 
from PIL import Image

db = geocoder.database()
# for key in db.keys():
  # print()
locations = geocoder.all_locations(db)
locList = []
usaLocList = {}
for location in locations:
  locList.append(location)
  if location.region == 'USA':
    usaLocList[location.name] = location

#####################################
#setup GLOBALs time and sun calculations
utc = pytz.UTC

#####################################
# setup GLOBALs design: tower hight in meters, mirror dimensions and list of reflectors
DistanceToSun = 10200 # far away so all rays are parallel
PanelWidth = 10
PanelHeight = 10
PanelRadius = 6
PoleHeight = 10 #hight above ground of the panels
Size = 400 #size of the domain with tower in center
# make a simple spiral for testing
# front of mirror
PanelPov = "    texture {pigment {color rgb <1,1,1>} finish {diffuse 0 ambient 0.01 reflection 1.0 phong 1 phong_size 100}}\n"
# back of mirror which could be customized
BlackPov = "    texture {pigment {color rgb <0,0,0>} finish {diffuse 0 ambient 0.00 reflection 0.0 phong 0 phong_size 0}}\n"
#we put a yellow ball around the sun so we can see it
SunPov = "//sun\nlight_source{ <0,0,0> color rgb<1,1,1>\n   looks_like{ sphere{<0.000, 0.000, 0.000>, 3.000\n       texture{pigment{color Yellow} finish{ambient 0.75 diffuse 2.0}}}}\n translate <%.3f, %.3f, %.3f>}\n"
CameraPov = "//camera\ncamera {orthographic right 150 up 150\n   location <%.3f, %.3f, %.3f>\n    look_at <0.000, 0.000, 000.000>\n  rotate<0, 0, 0> }\n"


def deleteFiles(dirObject , dirPath):
    if dirObject.is_dir(follow_symlinks=False):
        name = os.fsdecode(dirObject.name)
        newDir = dirPath+"/"+name
        moreFiles = os.scandir(newDir)
        for file in moreFiles:
            if file.is_dir(follow_symlinks=False):
                deleteFiles(file, newDir)
                os.rmdir(newDir+"/"+os.fsdecode(file.name))
            else:
                os.remove(newDir+"/"+os.fsdecode(file.name))
        os.rmdir(newDir)
    else:
        os.remove(dirPath+"/"+os.fsdecode(dirObject.name))

def clearPath(dataPath):
    if os.path.exists(dataPath):
        for file in os.scandir(dataPath):
            deleteFiles(file, dataPath)
    else:
        os.makedirs(dataPath)



class CityVisualizer:
    def __init__(self, cityName):
        if not cityName in usaLocList:
            sys.exit("An invalid cityname was given to city visualizer")
        self.city = usaLocList[cityName]
        self.timeZone = timezone(self.city.timezone)
        self.dataPath = "./reflector/" + cityName + "/"
        clearPath(self.dataPath)

    def povDrawSun(self,dayTime):
        # draws the sun
        sunPoint = tuple([i * DistanceToSun for i in self.sunVector(dayTime)])
        with open(self.filePath(dayTime), 'a') as fp:
            fp.write(SunPov % sunPoint)   

    def povDrawPanel(self,dayTime, point):
        # bisect vector
        sunV = self.sunVector(dayTime)
        # location of the mirror center
        centerP = tuple(map(operator.add, point, (0 , 0, PoleHeight)))
        centerBelowP = tuple(map(operator.add, point, (0 , 0, PoleHeight-0.1)))
        bisectV = tuple(map(operator.add, sunV, centerP))
        # make the mirror
        half = (PanelWidth/2, PanelHeight/2,0)
        cornerLL = tuple(map(operator.sub, sunV, half))
        cornerUR = tuple(map(operator.add, sunV, half))
        
        # rotations of mirror to face the bisect vector
        #https://groups.google.com/forum/#!topic/comp.graphics.algorithms/vuHUqZnYxtA
        (x, y, z) = self.unitVector(sunV)
        azimuth = -1*math.degrees(math.atan2(x,y)) # rotate around the z axis
        elevation = -1*math.degrees(math.acos(z)) # rotate around the x axis
        # top mirror surface
        with open(self.filePath(dayTime), 'a') as fp:
            fp.write("//mirror\nbox{ <%.3f, %.3f, %.3f>, <%.3f, %.3f, %.3f>\n" % (cornerLL + cornerUR))
            fp.write(PanelPov)
            fp.write("    rotate <%.3f, %.3f, %.3f>\n" % (elevation,0,0))
            fp.write("    rotate <%.3f, %.3f, %.3f>\n" % (0,0,azimuth))
            fp.write("    translate <%.3f, %.3f, %.3f>}\n" % centerP)
        #back of mirror surface (black)
        # with open(filePath(dayTime), 'a') as fp:
        #     fp.write("//mirror\nbox{ <%.3f, %.3f, %.3f>, <%.3f, %.3f, %.3f>\n" % (cornerLL + cornerUR))
        #     fp.write(BlackPov)
        #     fp.write("    rotate <%.3f, %.3f, %.3f>\n" % (elevation,0,0))
        #     fp.write("    rotate <%.3f, %.3f, %.3f>\n" % (0,0,azimuth))
        #     fp.write("    translate <%.3f, %.3f, %.3f>}\n" % centerBelowP)   
        # # draw pole supporting mirror 
        # with open(filePath(dayTime), 'a') as fp:
        #    # fp.write("// tower\nsphere{<%.3f, %.3f, %.3f>, %.3f\n"  % (0, 0, TowerHeight, TowerRadius))
        #    # fp.write("   texture{pigment{color White} \n   finish{ambient 0.15 diffuse 2.0}}}\n")
        #    fp.write("//pole\ncylinder{<%.3f, %.3f, %.3f>, <%.3f, %.3f, %.3f>, %.3f\n"  % (mirrorP +  centerP + (0.5,)))
        #    fp.write("   texture{pigment{color White} \n   finish{ambient 0.15 diffuse 2.0}}}\n")

                    
    def povDrawVector(self,dayTime, vector, offset, color = 'red'):
        with open(self.filePath(dayTime), 'a') as fp:
            toP = tuple(map(operator.add, vector, offset))
            fp.write("cylinder{<%.3f, %.3f, %.3f>, <%.3f, %.3f, %.3f>, %.3f\n"  % (offset + toP + (1,)))
            fp.write("   texture{pigment{color %s} \n   finish{ambient 0.15 diffuse 2.0}}}\n" % (color,))
            
    def povDrawGround(self,dayTime):
        half = (Size/2, Size/2,0)
        cornerLL = tuple(map(operator.sub, (0,0,0), half))
        cornerUR = tuple(map(operator.add, (0,0,0), half))
        with open(self.filePath(dayTime), 'a') as fp:
            fp.write("//ground\nbox{ <%.3f, %.3f, %.3f>, <%.3f, %.3f, %.3f>\n" % (cornerLL + cornerUR))
            fp.write("    texture{pigment{color YellowGreen}}}\n")
        
    def povSetup(self,dayTime):
        # delete old and create new
        sunPoint = tuple([i * 200 for i in self.sunVector(dayTime)])
        if os.path.exists(self.filePath(dayTime)):
            os.remove(self.filePath(dayTime)) 
        with open(self.filePath(dayTime), 'w') as fp:
            fp.write("#include \"colors.inc\"\n#include \"textures.inc\"\n")
            fp.write(CameraPov % sunPoint)
    
    def filePath(self,dayTime):
        return self.dataPath + dayTime.strftime('%Y_%m_%d_%H_%M') + '.pov'
                
    def sunPosition(self,dayTime):
        obs = self.city.observer 
        azimuth = astral.sun.azimuth(observer=obs, dateandtime=dayTime)
        elevation = astral.sun.elevation(observer=obs, dateandtime=dayTime)
        return (math.radians(elevation), math.radians(azimuth))
        
    def sunVector(self,dayTime):
        # https://math.stackexchange.com/questions/1150232/finding-the-unit-direction-vector-given-azimuth-and-elevation
        (elevation, azimuth) = self.sunPosition(dayTime)
        return (math.sin(azimuth) * math.cos(elevation), math.cos(azimuth) * math.cos(elevation), math.sin(elevation))
        
    def visualizeLayout(self,dayTime, points):
        # generate a pov ray file named for this date and time
        
        #need to update the camera before calling povSetup
        self.povSetup(dayTime) #create file and add includes
        self.povDrawGround(dayTime) # put in ground
        self.povDrawSun(dayTime) # sun
        for point in points:
            self.povDrawPanel(dayTime, point)

    def oneDaySimulation(self,points,dayTime=None, sampleTime = 60):
        #computes the POVray file sequence for different times this dayTime
        if dayTime is None:
            dayTime = datetime(2019, 6, 21, 0, 0, 0, 0, self.timeZone)
        obs = self.city.observer
        sun = astral.sun.sun(observer=obs, date=dayTime)
        # start 20 minutes after sunrise and end 20 minutes before sunset
        sunRise = relativedelta(minutes=+20) + sun['sunrise'].replace(second=0, microsecond=0).astimezone(self.timeZone)
        sunSet =  relativedelta(minutes=-20) + sun['sunset'].replace(second=0, microsecond=0).astimezone(self.timeZone)
        # loop through each time sample
        for sample in range(0,24*60//sampleTime):
            dayTime = dayTime + relativedelta(minutes=+sampleTime)
            if (dayTime >= sunRise and dayTime <= sunSet):
                self.visualizeLayout(dayTime, points)

    def generalSimulation(self, points, sampleTime):
        daytimes = [datetime(2020,6,21,0,0,0, 0, self.timeZone), datetime(2020,12,21,0,0,0,0, self.timeZone), datetime(2020,9,21,0,0,0,0,self.timeZone)]
        for daytime in daytimes:
            oneDaySimulation(points, dayTime=daytime, sampleTime=sampleTime)


    def oneYearSimulation(self,points,year = 2019, sampleTime = 60, sampleDays = 30):
        # generate pov sequence for each of these days
        zeroDay = datetime(year, 1, 1, 0, 0, 0, 0, self.timeZone)
        allDays =  [zeroDay + timedelta(days=x) for x in range(0, 365, sampleDays)] 
        for dayTime in allDays:
            self.oneDaySimulation(points, dayTime,sampleTime)

    # utilities
    def multiVector(self,vector, magnitude):
        return tuple([i * magnitude for i in list(vector)])
        
    def unitVector(self,v):
        size = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
        return tuple([i/size for i in list(v)])
        
    def vectorUnit(self,v):
        l=  math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
        return tuple([c/l for c in v])

    def process(self):
        #step 1) Add "C:\Program Files\POV-Ray\v3.7\bin" to your environment variables path. (Hopefully the target is the same for your computer)
        #step 2) open up povray.
        #step 3) go to "options", and disable "keep single instance"
        #step 4) run this code! it should work!
        start = datetime.now()
        print(start)
        # subprocess.call("cd", shell=True)
        os.chdir(os.path.abspath(os.path.expanduser(self.dataPath))) #navigate to the target folder with the pov files.
        #Depending on where you put this file, you might need to change

        povFiles = glob.glob("*.pov")
        print(len(povFiles))
        pngFiles = []
        threshhold = 5
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
        os.chdir(os.path.abspath("../.."))
        end = datetime.now()
        duration = end-start 
        print(duration)
        return sunPixels




