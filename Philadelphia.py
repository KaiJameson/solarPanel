import numpy as np
import math
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import matplotlib.pyplot as plt
import os.path
import operator
from dateutil.relativedelta import relativedelta

from astral import geocoder
from astral import location
import astral

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
  # print(location)
# print(locList[0].name)
CityName = 'Philadelphia' #Aberdeen' # 'Honolulu' # 'Nairobi'
City = usaLocList[CityName]


#####################################
#setup GLOBALs time and sun calculations
utc = pytz.UTC
# astral = Astral()
# astral.solar_depression = 'civil'
# CityName = AllCities[10] #pick the city
# City = astral[CityName]
TimeZone = timezone(City.timezone)
DataPath = "./reflector/" + CityName + "/"
# DataPath = 'C:/Users/Nicholas Flann/Dropbox/LEEDtracker/reflector/'+ CityName + '/'
#DataPath = 'C:/Users/nickf/Dropbox/LEEDtracker/reflector/' + CityName + '/'
if not os.path.exists(DataPath):
    os.makedirs(DataPath)

#####################################
# setup GLOBALs design: tower hight in meters, mirror dimensions and list of reflectors
DistanceToSun = 10200 # far away so all rays are parallel
MirrorWidth = 10
MirrorHeight = 10
MirrorRadius = 6
PoleHeight = 10 #hight above ground of the mirrors
Size = 400 #size of the domain with tower in center
# make a simple spiral for testing
MirrorsPer = 16
Rotations =4
MirrorPolar = [(math.radians(360*(i%MirrorsPer)/(1.0*MirrorsPer)), 20 + 100.0*i/(MirrorsPer*Rotations)) for i in range(0,MirrorsPer*Rotations)]
MirrorPoints = [(r*math.cos(angle), r*math.sin(angle), 0) for (angle, r) in MirrorPolar]
# front of mirror
MirrorPov = "    texture {pigment {color rgb <1,1,1>} finish {diffuse 0 ambient 0.01 reflection 1.0 phong 1 phong_size 100}}\n"
# back of mirror which could be customized
BlackPov = "    texture {pigment {color rgb <0,0,0>} finish {diffuse 0 ambient 0.00 reflection 0.0 phong 0 phong_size 0}}\n"
#we put a yellow ball around the sun so we can see it
SunPov = "//sun\nlight_source{ <0,0,0> color rgb<1,1,1>\n   looks_like{ sphere{<0.000, 0.000, 0.000>, 3.000\n       texture{pigment{color Yellow} finish{ambient 0.75 diffuse 2.0}}}}\n translate <%.3f, %.3f, %.3f>}\n"
#just for debugging from the side
#just for debugging from the top
#CameraPov = "//camera\ncamera {orthographic angle 60\n   location <0.000, 400.000, 00.000>\n    look_at <0.000, 0.000, 000.000>\n  rotate<90, 0, 0> }\n"
# for debugging at the tower top
# CameraPov = "//camera\ncamera {fisheye angle 120\n   location <%.3f, %.3f, %.3f>\n    look_at <0.000, 0.000, 000.000>\n  rotate<90, 0, 0> }\n"
CameraPov = "//camera\ncamera {fisheye angle 120\n   location <%.3f, %.3f, %.3f>\n    look_at <0.000, 0.000, 000.000>\n  rotate<0, 0, 0> }\n"
#Draws the primary lightsource (sun) at <x,y,z>...     
def povDrawSun(dayTime):
    # draws the sun
    sunPoint = tuple([i * DistanceToSun for i in sunVector(dayTime)])
    with open(filePath(dayTime), 'a') as fp:
        fp.write(SunPov % sunPoint)   

def povDrawMirror(dayTime, mirrorP):
    # bisect vector
    sunV = sunVector(dayTime)
    # location of the mirror center
    centerP = tuple(map(operator.add, mirrorP, (0 , 0, PoleHeight)))
    centerBelowP = tuple(map(operator.add, mirrorP, (0 , 0, PoleHeight-0.1)))
    bisectV = tuple(map(operator.add, sunV, centerP))
    # make the mirror
    half = (MirrorWidth/2, MirrorHeight/2,0)
    cornerLL = tuple(map(operator.sub, sunV, half))
    cornerUR = tuple(map(operator.add, sunV, half))
    
    # DEBUG
    # povDrawVector(dayTime, multiVector(sunV, 20), center, color = 'Red')
    # povDrawVector(dayTime, multiVector(towerV, 50), center, color = 'Green')
    # povDrawVector(dayTime, multiVector(bisectV, 20), center, color = 'Blue')
    # rotations of mirror to face the bisect vector
    #https://groups.google.com/forum/#!topic/comp.graphics.algorithms/vuHUqZnYxtA
    (x, y, z) = unitVector(sunV)
    azimuth = -1*math.degrees(math.atan2(x,y)) # rotate around the z axis
    elevation = -1*math.degrees(math.acos(z)) # rotate around the x axis
    # top mirror surface
    with open(filePath(dayTime), 'a') as fp:
        fp.write("//mirror\nbox{ <%.3f, %.3f, %.3f>, <%.3f, %.3f, %.3f>\n" % (cornerLL + cornerUR))
        fp.write(MirrorPov)
        fp.write("    rotate <%.3f, %.3f, %.3f>\n" % (elevation,0,0))
        fp.write("    rotate <%.3f, %.3f, %.3f>\n" % (0,0,azimuth))
        fp.write("    translate <%.3f, %.3f, %.3f>}\n" % centerP)
    #back of mirror surface (black)
    with open(filePath(dayTime), 'a') as fp:
        fp.write("//mirror\nbox{ <%.3f, %.3f, %.3f>, <%.3f, %.3f, %.3f>\n" % (cornerLL + cornerUR))
        fp.write(BlackPov)
        fp.write("    rotate <%.3f, %.3f, %.3f>\n" % (elevation,0,0))
        fp.write("    rotate <%.3f, %.3f, %.3f>\n" % (0,0,azimuth))
        fp.write("    translate <%.3f, %.3f, %.3f>}\n" % centerBelowP)   
    # draw pole supporting mirror 
    with open(filePath(dayTime), 'a') as fp:
       # fp.write("// tower\nsphere{<%.3f, %.3f, %.3f>, %.3f\n"  % (0, 0, TowerHeight, TowerRadius))
       # fp.write("   texture{pigment{color White} \n   finish{ambient 0.15 diffuse 2.0}}}\n")
       fp.write("//pole\ncylinder{<%.3f, %.3f, %.3f>, <%.3f, %.3f, %.3f>, %.3f\n"  % (mirrorP +  centerP + (0.5,)))
       fp.write("   texture{pigment{color White} \n   finish{ambient 0.15 diffuse 2.0}}}\n")

        
def povDrawDisk(dayTime, point):
    # bisect vector
    sunV = sunVector(dayTime)
    towerV = towerVector(point)
    bisectV = tuple(map(operator.add, sunV, towerV))
    # location of the mirror center
    center = tuple(map(operator.add, point, (0 , 0, PoleHeight)))
    offset = tuple(map(operator.add, center, unitVector(bisectV)))
    #  DEBUG
    # povDrawVector(dayTime, multiVector(sunV, 20), center, color = 'Red')
    # povDrawVector(dayTime, multiVector(towerV, 50), center, color = 'Green')
    # povDrawVector(dayTime, multiVector(bisectV, 20), center, color = 'Blue')
    # rotations of mirror to face the bisect vector
    #https://groups.google.com/forum/#!topic/comp.graphics.algorithms/vuHUqZnYxtA
    with open(filePath(dayTime), 'a') as fp:
        fp.write("//mirror disk\ncylinder{ <%.3f, %.3f, %.3f>, <%.3f, %.3f, %.3f>, %.3f\n" % (center + offset + (MirrorRadius,)))
        fp.write(MirrorPov + '}\n')
        
def povDrawVector(dayTime, vector, offset, color = 'red'):
    # DEBUG! DRAW EACH VECTOR AS A ROD
    with open(filePath(dayTime), 'a') as fp:
       # fp.write("// tower\nsphere{<%.3f, %.3f, %.3f>, %.3f\n"  % (0, 0, TowerHeight, TowerRadius))
       # fp.write("   texture{pigment{color White} \n   finish{ambient 0.15 diffuse 2.0}}}\n")
       toP = tuple(map(operator.add, vector, offset))
       #print(offset + toP + (1,))
       fp.write("cylinder{<%.3f, %.3f, %.3f>, <%.3f, %.3f, %.3f>, %.3f\n"  % (offset + toP + (1,)))
       fp.write("   texture{pigment{color %s} \n   finish{ambient 0.15 diffuse 2.0}}}\n" % (color,))
        
def povDrawGround(dayTime):
    half = (Size/2, Size/2,0)
    cornerLL = tuple(map(operator.sub, (0,0,0), half))
    cornerUR = tuple(map(operator.add, (0,0,0), half))
    with open(filePath(dayTime), 'a') as fp:
        fp.write("//ground\nbox{ <%.3f, %.3f, %.3f>, <%.3f, %.3f, %.3f>\n" % (cornerLL + cornerUR))
        fp.write("    texture{pigment{color YellowGreen}}}\n")
    
def povSetup(dayTime):
    # delete old and create new
    sunPoint = tuple([i * 200 for i in sunVector(dayTime)])
    if os.path.exists(filePath(dayTime)):
        os.remove(filePath(dayTime)) 
    with open(filePath(dayTime), 'w') as fp:
        fp.write("#include \"colors.inc\"\n#include \"textures.inc\"\n")
        fp.write(CameraPov % sunPoint)
 
def filePath(dayTime):
    return DataPath + dayTime.strftime('%Y_%m_%d_%H_%M') + '.pov'
            
def sunPosition(dayTime):
    obs = City.observer 
    azimuth = astral.sun.azimuth(observer=obs, dateandtime=dayTime)
    elevation = astral.sun.elevation(observer=obs, dateandtime=dayTime)
    return (math.radians(elevation), math.radians(azimuth))
    
def sunVector(dayTime):
    # https://math.stackexchange.com/questions/1150232/finding-the-unit-direction-vector-given-azimuth-and-elevation
    (elevation, azimuth) = sunPosition(dayTime)
    return (math.sin(azimuth) * math.cos(elevation), math.cos(azimuth) * math.cos(elevation), math.sin(elevation))
    
def generateSolarCollector(dayTime):
    # generate a pov ray file named for this date and time
    # all mirrors are positioned to reflect the sun to the tower
    
    #need to update the camera before calling povSetup
    povSetup(dayTime) #create file and add includes
    povDrawGround(dayTime) # put in ground
    # povDrawTower(dayTime) # tower 
    povDrawSun(dayTime) # sun
    for mirrorP in MirrorPoints:
        #povDrawDisk(dayTime, mirrorP) # alternative round reflector
        povDrawMirror(dayTime, mirrorP)

def oneDaySimulation(dayTime, sampleTime = 60):
    #computes the POVray file sequence for different times this dayTime
    timeZone = timezone(City.timezone)
    obs = City.observer
    sun = astral.sun.sun(observer=obs, date=dayTime)
    # start 20 minutes after sunrise and end 20 minutes before sunset
    sunRise = relativedelta(minutes=+20) + sun['sunrise'].replace(second=0, microsecond=0).astimezone(timeZone)
    sunSet =  relativedelta(minutes=-20) + sun['sunset'].replace(second=0, microsecond=0).astimezone(timeZone)
    # loop through each time sample
    for sample in range(0,24*60//sampleTime):
        dayTime = dayTime + relativedelta(minutes=+sampleTime)
        if (dayTime >= sunRise and dayTime <= sunSet):
            #print "Animation = "+str(dayTime)
            generateSolarCollector(dayTime)
            
def oneYearSimulation(year = 2019, sampleTime = 60, sampleDays = 30):
    # generate pov sequence for each of these days
    zeroDay = datetime(year, 1, 1, 0, 0, 0, 0, TimeZone)
    allDays =  [zeroDay + timedelta(days=x) for x in range(0, 365, sampleDays)] 
    for dayTime in allDays:
        oneDaySimulation(dayTime, sampleTime)

# utilities
def multiVector(vector, magnitude):
    return tuple([i * magnitude for i in list(vector)])
    
def unitVector(v):
    size = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return tuple([i/size for i in list(v)])
    
def vectorUnit(v):
    l=  math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return tuple([c/l for c in v])
######################################################
testDay = datetime(2019, 6, 21, 0, 0, 0, 0, TimeZone)
oneDaySimulation(testDay, 5)
# oneYearSimulation(sampleDays=5);

