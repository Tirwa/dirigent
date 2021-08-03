# Dirigent - multi media player director

### TODO
# establich connection to playerctl - DONE
# get list of players - DONE
# parse yaml file - DONE
# create routines for common start/stop/play scenarios - DONE
# learn about time - DONE
# idea: every two seconds (sleep 2), check if something should be playing - DONE for now, respects SLEEPTIME and MAXTICK
# idea: create yaml verification via flag, set a bool to just try and read the yaml file and print the media slots
# switchover: variable to be set if the player needs to be monitored
#             if it is set, the main loop needs to continuously check that player
#             as soon as it stops, the next item needs to be started

import distutils.spawn
import subprocess
import argparse
import os.path
import yaml
from time import sleep, localtime

VERSION = "0.0.5"
PLAYERCTL = ""
VLC = ""
MOPIDY = ""
STARTUP = True
SLEEPTIME = 2
MAXTICK = 1

parser = argparse.ArgumentParser(description='Dirigent - a media player orchestration tool. Reads a yaml file to understand what they need to do.')
parser.add_argument('yamlFile')
args = parser.parse_args()

def playMedia(args):
    mediaFile = ''
    mediaStream = ''
    print("Stopping Playback ...")
    stopMedia()
    print("Trying to play " + str(args) + " ...")

    try:    #look for a file in the arguments
        mediaFile = args['file']
        print(mediaFile)
    except KeyError:
        print("No File in directions!")
    
    try:    # look for a stream in the arguments
        mediaStream = args['stream'] 
        #print(mediaStream)
    except KeyError: 
        print("No Stream in directions!")
    
    if(mediaFile):
        print("Calling VLC now ...")
    if(mediaStream):
        print("Calling " + mediaStream + " now ...")
        if(PLAYERCTL):
            playerctlStartProcess = subprocess.run([PLAYERCTL, "-p", mediaStream, "play"], capture_output=True)

def stopMedia():
    if(PLAYERCTL):
        playertctlStopProcess = subprocess.run([PLAYERCTL, "-a", "pause"])

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
                playlist = list(loadedYaml['playlist'])
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
       
## main loop       
if(STARTUP):
    #print(playlist)
    print("Found the following media slots ...")
    timeslots = {}
    for slot in playlist:
        #print(slot.values[0])
        slotTitle = list(slot)[0]
        slotAttributes = list(slot.values())[0]
        try:
            print(slotTitle + " @ " + slotAttributes['start'])
            timeslots[slotAttributes['start']] = slotTitle
        except KeyError:
            pass
    currentTick = 0
    while (currentTick < MAXTICK):
        timeNow = localtime()
        currentTimeString = str(timeNow.tm_hour) + ":" + str(timeNow.tm_min)
        try:
            startMedia = timeslots[currentTimeString]
            print(startMedia)
            playMedia("")            
        except KeyError:
            print("Nothing to start!")    
            playMedia(playlist[2]['filler']) # this is here just for debugging, remove later
        #print(currentTimeString)
        currentTick = currentTick + 1
        sleep(SLEEPTIME)


print("Dirigent v" + VERSION + " has shut down!")