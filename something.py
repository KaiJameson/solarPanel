import os
import subprocess

#step 1) Add "C:\Program Files\POV-Ray\v3.7\bin" to your environment variables path. (Hopefully the target is the same for your computer)
#step 2) open up povray.
#step 3) go to "options", and disable "keep single instance"
#step 4) run this code! it should work!

subprocess.call("cd", shell=True)
os.chdir(os.path.abspath(os.path.expanduser('reflector/Philadelphia'))) #navigate to the target folder with the pov files.
#Depending on where you put this file, you might need to change
my_env = os.environ.copy()
my_env["PATH"] = "C:/Program Files/POV-Ray/v3.7/bin;" + my_env["PATH"]

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