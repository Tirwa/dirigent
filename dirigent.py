# Dirigent - multi media player director

### TODO
# establich connection to playerctl - DONE
# get list of players - DONE
# parse yaml file - DONE
# learn about time
# create routines for common start/stop/play scenarios

import distutils.spawn
import subprocess
import argparse
import os.path
import yaml

VERSION = "0.0.3"
PLAYERCTL = ""
VLC = ""
MOPIDY = ""
STARTUP = True

parser = argparse.ArgumentParser(description='Dirigent - a media player orchestration tool. Reads a yaml file to understand what they need to do.')
parser.add_argument('yamlFile')
args = parser.parse_args()

print("Dirigent v" + VERSION + " starting up ...")

## checking and opening yaml 
if(STARTUP):
    print("Checking File " + args.yamlFile + " ...")
    if (args.yamlFile[-3:] == "yml"):
        try:
            yamlFile = open(args.yamlFile)
            print("YAML File found!")
            loadedYaml = yaml.safe_load(yamlFile)
            #print(loadedYaml)
            try:
                playlist = loadedYaml['playlist']
                #print(playlist)                
            except (AttributeError, KeyError) as e:
                print("Error: No Playlist found in file!")
                STARTUP = False
        except IOError:
            print("Error: Couldn't open the YAML file!")
            STARTUP = False
    else:
        print("This does not look like a YAML file!")
        STARTUP = False    
    
## checking for playerctl and trying to get a list of available players
if(STARTUP):
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

## checking for vlc
if(STARTUP):
    print("Looking for vlc ...")
    VLC = distutils.spawn.find_executable("vlc")    
    if (VLC):
        print ("vlc found at " + VLC)    
    else:
        print ("Error: Unable to locate vlc!")
        STARTUP = False
        
if(STARTUP):
    print("Main Loop :)")
    #print(playlist)
    for slot in playlist:
        print(slot)



print("Dirigent v" + VERSION + " has shut down!")