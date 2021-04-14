import os
import subprocess

#step 1) Add "C:\Program Files\POV-Ray\v3.7\bin" to your environment variables path. (Hopefully the target is the same for your computer)
#step 2) open up povray.
#step 3) go to "options", and disable "keep single instance"
#step 4) run this code! it should work!

subprocess.call("cd", shell=True)
os.chdir(os.path.abspath(os.path.expanduser('reflector/Wilmington'))) #navigate to the target folder with the pov files.
#Depending on where you put this file, you might need to change
my_env = os.environ.copy()
# my_env["PATH"] = "C:/Program Files/POV-Ray/v3.7/bin;" + my_env["PATH"]

for i in range(5,12):
    #subprocess.run("pvengine 2019_06_21_06_00.pov",shell=True, capture_output = True, text = True, env = my_env)
    #subprocess.check_output("run pvengine 2019_06_21_06_00.pov", shell=True, stderr = subprocess.PIPE, env=my_env)
    #subprocess.call("start pvengine 2019_06_21_0"+str(i)+"_00.pov", shell=True, env=my_env)
    for j in range(0,60,5):
        result = subprocess.Popen(f"start pvengine 2019_06_21_{i:02d}_{j:02d}.pov -d /exit", shell=True, env=my_env)

    # the -d tag prevents povray from displaying the png render, just to save time
    # the /exit tag exits out of pvengine after it is done rendering
    #result.wait()
    #result.terminate()
def createPNGFiles(sampleTime = 60):
    #subprocess.call("cd", shell=True)
    os.chdir(os.path.abspath(os.path.expanduser('reflector/Wilmington')))  # navigate to the target folder with the pov files.
    istart = 4
    iend = 21
    jstart = 0
    jend = 60
    jinc = sampleTime
    for j in range(jstart, jend, jinc):
        files = []
        for i in range(istart, iend):
            if (os.path.isfile(f"2019_06_21_{i:02d}_{j:02d}.pov") == False): #dont render if the pov file doesnt exist (duh)
                continue
            if (os.path.isfile(f"2019_06_21_{i:02d}_{j:02d}.png") == True): #dont render if the png file already exist (duh)
                continue
            subprocess.Popen(f"start pvengine 2019_06_21_{i:02d}_{j:02d}.pov -d /exit",shell=True)
            files.append([i,j])
        # wait for the processes to finish
        done = False
        while (not done):
            done = True
            #files = [os.path.isfile(f"2019_06_21_{i:02d}_{j:02d}.png") for i in range(istart, iend)]
            for k in range(len(files)):
                if os.path.isfile(f"2019_06_21_{files[k][0]:02d}_{files[k][1]:02d}.png") == False:
                    done = False
    time.sleep(1)
    print("PNG files created")

def computeScore(sampleTime = 60):
    if (not os.path.split(os.getcwd())[-1] == "Wilmington"):
        os.chdir(os.path.abspath(os.path.expanduser('reflector/Wilmington')))  # navigate to the target folder with the pov files.
    istart = 4
    iend = 21
    jstart = 0
    jend = 60
    jinc = sampleTime
    totalPixels = 0;
    framesun = []
    for m in range(jstart, jend, jinc):
        for n in range(istart, iend):
            if (os.path.isfile(f"2019_06_21_{n:02d}_{m:02d}.png") == False):
                continue
            # load the image
            image = Image.open(f'2019_06_21_{n:02d}_{m:02d}.png')
            # convert image to numpy array
            data = asarray(image)
            totalPixels = len(data) * len(data[0])
            sunPixels = 0
            for i in range(len(data)):
                for j in range(len(data[0])):
                    k = 0;  # k is the red channel
                    if (data[i][j][k] > 220):
                        sunPixels += 1
            framesun.append(sunPixels)

    finalScore = 0
    for i in range(len(framesun)):
        finalScore += framesun[i]
    finalScore /= (totalPixels * len(framesun))
    print("Final Score computed: " + str(finalScore))