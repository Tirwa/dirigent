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
import argparse


parser = argparse.ArgumentParser(description='Dirigent - a media player orchestration tool. Reads a yaml file to understand what they need to do.')
parser.add_argument('yamlFile')
args = parser.parse_args()
print("Dirigent v" + VERSION + " starting up ...")
print("Checking File " + args.yamlFile + " ...")

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