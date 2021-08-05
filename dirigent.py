# Dirigent - multi media player director

### TODO
# establich connection to playerctl - DONE
# get list of players - DONE
# parse yaml file - DONE
# create routines for common start/stop/play scenarios - DONE
# learn about time - DONE
# idea: every two seconds (sleep 2), check if something should be playing - DONE for now, respects SLEEPTIME and MAXTICK
# idea: create yaml verification via flag, set a bool to just try and read the yaml file and print the media slots
# idea: create yaml structure (variable: loopvideo) to allow loop flag for vlc for combined video/stream playback
# switchover: variable to be set if the player needs to be monitored
#             if it is set, the main loop needs to continuously check that player
#             as soon as it stops (playerctl status returns "Stopped"), the next item needs to be started - DONE, tested
# fix: streams without a start time are currently only started via failover, so a stream at the beginning of file can not be played - DONE
# fix: time components (minute / hour) have leading zeroes omitted, causing some start times to be ignored - DONE
# idea: since playerctl won't play a file in vlc if it's not running, add a routine to check if it is running and if necessary, start it (maybe giving along options with branding overlay)
# cvlc --fullscreen --video-on-top --x11-display :0 <file> &
# this keeps the vlc process running, even if it doesn't show anything after the file finishes - it still reports as "Stopped" for switchover, and opening another file via "playerctl open" works fine

import distutils.spawn
import subprocess
import argparse
import os.path
import yaml
from time import sleep, localtime

VERSION = "0.0.6"
PLAYERCTL = ""
VLC = ""
MOPIDY = ""
STARTUP = True
SLEEPTIME = 2
MAXTICK = 10000
SWITCHOVER = []
LINEWIDTH = 72

parser = argparse.ArgumentParser(description='Dirigent - a media player orchestration tool. Reads a yaml file to understand what they need to do.')
parser.add_argument('yamlFile')
args = parser.parse_args()

def playMedia(args):
    global SWITCHOVER
    mediaFile = ''
    mediaStream = ''
    print("Stopping Playback ...")
    stopMedia()
    print("Trying to play " + str(args) + " ...")
    try:    #look for switchover
        switchoverFlag = args['switchover']
        if(switchoverFlag):
            SWITCHOVER = ['vlc', True]
        else:
            SWITCHOVER = []
    except KeyError:
        SWITCHOVER = []
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
        playVlcFile(mediaFile)
        try:
            setVlcLoop(args['loopvideo'])
        except KeyError:
            setVlcLoop(False)

    if(mediaStream):
        print("Calling " + mediaStream + " now ...")
        if(PLAYERCTL):
            playerctlStartProcess = subprocess.run([PLAYERCTL, "-p", mediaStream, "play"])

def setVlcLoop(boolLoop):
    if(PLAYERCTL):
        if(boolLoop):
            playerctlVlcLoopInstructions = [PLAYERCTL, "-p", "vlc", "loop", "Track"]
        else:
            playerctlVlcLoopInstructions = [PLAYERCTL, "-p", "vlc", "loop", "None"]
        playerctlVlcLoopProcess = subprocess.run(playerctlVlcLoopInstructions)
        
def stopMedia():
    if(PLAYERCTL):
        playertctlStopProcess = subprocess.run([PLAYERCTL, "-a", "pause"])

def getVlcStatus():
    if(PLAYERCTL):
        playerctlVlcCheckProcess = subprocess.run([PLAYERCTL, "-p", "vlc", "status"], capture_output=True)
        playerctlVlcStdout = playerctlVlcCheckProcess.stdout.decode('UTF-8')[:-1].split(',')
        return str(playerctlVlcStdout[0])

def getPlaylistIndex(slotName):
    for slot in enumerate(playlist):
        try:
            testIndex = slot[1][slotName]
            return slot[0]
        except KeyError:
            pass

def playVlcFile(fileName):
    if(PLAYERCTL):
        playerctlVlcPlayInstructions = [PLAYERCTL, "-p", "vlc", "open", fileName]
        playerctlVlcPlayProcess = subprocess.run(playerctlVlcPlayInstructions)

def startVlcProcess():
    if(VLC):
        vlcStartInstructions = [VLC, "--fullscreen", "--video-on-top", "--x11-display", ":0"]
        vlcStartProcess = subprocess.Popen(vlcStartInstructions)

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

## checking for vlc
if(STARTUP):
    print("Looking for vlc ...")
    VLC = distutils.spawn.find_executable("cvlc")    
    if (VLC):
        print ("vlc found at " + VLC)    
    else:
        print ("Error: Unable to locate vlc!")
        STARTUP = False

## checking for playerctl and making sure vlc is running
if(STARTUP):
    print("Looking for playerctl ...")
    PLAYERCTL = distutils.spawn.find_executable("playerctl")
    if (PLAYERCTL):
        print ("playerctl found at " + PLAYERCTL)
        print("Getting List of all available media players ...")
        playerctlProcess = subprocess.run([PLAYERCTL, "--list-all"], capture_output=True)
        playerctlStdout = playerctlProcess.stdout.decode('UTF-8').splitlines()
        print(playerctlStdout)
        try:
            vlcStarted = playerctlStdout.index('vlc')
        except ValueError:
            startVlcProcess()
    else:
        print ("Error: Unable to locate playerctl!")
        STARTUP = False


       
## main loop       
if(STARTUP):
    #print("-- Main Loop --")
    print("Found the following media slots ...")
    timeslots = {}
    for slot in playlist:
        print(slot)
        slotTitle = list(slot)[0]
        slotAttributes = list(slot.values())[0]
        try:
            print(slotTitle + " @ " + slotAttributes['start'])
            timeslots[slotAttributes['start']] = slotTitle
        except KeyError:
            pass
    currentTick = 0
    while (currentTick < MAXTICK):
        print("-- Main Loop Tick --")   
        timeNow = localtime()
        currentTimeString = str(timeNow.tm_hour).rjust(2, '0') + ":" + str(timeNow.tm_min).rjust(2, '0')
        if(len(SWITCHOVER)>0):
            vlcStatus = getVlcStatus()
            if(vlcStatus == "Stopped"):
                print("Switchover! Starting stream!")
                playMedia({'stream': 'mopidy'})
            print("VLC Status for switchover: " + vlcStatus)
        else:
            try:
                print("Trying for media ... " + "currentTimeString: " + currentTimeString)
                startMedia = timeslots[currentTimeString]
                slotToPlay = playlist[getPlaylistIndex(startMedia)]
                print(str(slotToPlay[startMedia]))
                playMedia(slotToPlay[startMedia])            
            except KeyError:
                # check if the first entry in yaml is a stream without start?
                firstEntry = list(playlist[0].values())[0]
                try:
                    if(firstEntry['stream'] == 'mopidy' and currentTick == 0):
                        print("First Entry is a stream!")
                        try:
                            testStartTime = firstEntry['start']
                        except KeyError:
                            playMedia(firstEntry)
                except KeyError:
                    pass
                print("Nothing to start!")    
                #playMedia(playlist[6]['dinnerbreak']) # this is here just for debugging, remove later   playMedia(playlist[2]['filler'])
        currentTick = currentTick + 1
        sleep(SLEEPTIME)


print("Dirigent v" + VERSION + " has shut down!")