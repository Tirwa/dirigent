# Dirigent - multi media player director

### TODO
# establich connection to playerctl
# get list of players
# parse yaml files
# create routines for common start/stop/play scenarios

VERSION = "0.0.2"
PLAYERCTL = ""
VLC = ""
MOPIDY = ""
STARTUP = True









import distutils.spawn
import subprocess




print("Dirigent v" + VERSION + " starting up ...")


print("Looking for playerctl ...")
PLAYERCTL = distutils.spawn.find_executable("playerctl")
if (PLAYERCTL):
    print ("playerctl found at " + PLAYERCTL)
    print("Getting List of all available media players ...")
    playerctlProcess = subprocess.run([PLAYERCTL, "--list-all"], capture_output=True)
    playerctlStdout = playerctlProcess.stdout.decode('UTF-8')[:-1].split(',')
    print(playerctlStdout)
    if(playerctlStdout == ""):
        pass
else:
    print ("Error: Unable to locate playerctl!")
    STARTUP = False





if(STARTUP):
    print("Main Loop :)")











print("Dirigent v" + VERSION + " has shut down!")