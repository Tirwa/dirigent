# Dirigent - multi media player director

### TODO

# establich connection to playerctl - DONE
# get list of players - DONE
# parse yaml file - DONE
# create routines for common start/stop/play scenarios - DONE
# learn about time - DONE
# we OOP now, restructure code - DONE
# idea: every two seconds (sleep 2), check if something should be playing - DONE for now, respects SLEEPTIME and MAXTICK
# idea: create yaml verification via flag, set a bool to just try and read the yaml file and print the media slots - DONE, flag is --dryrun
# idea: create yaml structure (variable: loopvideo) to allow loop flag for vlc for combined video/stream playback
# switchover: variable to be set if the player needs to be monitored
#             if it is set, the main loop needs to continuously check that player
#             as soon as it stops (playerctl status returns "Stopped"), the next item needs to be started - DONE, tested
# fix: streams without a start time are currently only started via failover, so a stream at the beginning of file can not be played - DONE
# fix: time components (minute / hour) have leading zeroes omitted, causing some start times to be ignored - DONE
# feature: when starting the main loop, try to establish if something should be already playing, and start that - DONE, conflicted with switchover so PLAYBACK was added to be set when correctly playing files, thus preventing recovery in normal operation and only when restarting the tool
# test: absolute/relative paths in filenames
# added uri parsing for streams, doesn't fully work for now
# fixed: multiple startups of the same file in one minute




import argparse
import os.path
import yaml
from datetime import datetime, timedelta
from time import sleep, localtime

from playControls import PlayControls
from playlist import Playlist
from messaging import Messaging

VERSION = "0.1.0"

STARTUP = True
SLEEPTIME = 2
MAXTICK = 10000
MINUTEBUFFER = "00"

DRYRUN = False
DEBUG = True


parser = argparse.ArgumentParser(description='Dirigent - a media player orchestration tool. Reads a yaml file to understand what they need to do.')
parser.add_argument('yamlFile')
parser.add_argument('--dryrun', required=False, action='store_true', help="dryrun, just parse + verify the yaml without actually orchestrating media players")
args = parser.parse_args()

messageController = Messaging(DEBUG)            

messageController.message("Dirigent v" + VERSION + " starting up ...",0)

##detecting dryrun
DRYRUN = args.dryrun
messageController.message("DRYRUN: " + str(DRYRUN),0)
if DRYRUN : MAXTICK = 0

## checking and opening yaml 
playlistController = Playlist(args.yamlFile)
if (playlistController.initializePlaylist() != 0):
    STARTUP = False
playControls = PlayControls(messageController)
    
## checking for playerctl and trying to get a list of available players
if(STARTUP and not DRYRUN):
    messageController.message("Looking for playerctl ...",2)
    playerctlSetup = playControls.setupPlayerctl()
    if(int(playerctlSetup)>=0):
        messageController.message(playerctlSetup,2)
    else:
        messageController.message("Error: Unable to locate playerctl!",0)
        STARTUP = False

## checking for vlc
if(STARTUP and not DRYRUN):
    messageController.message("Looking for vlc ...",2)
    VLCstartup = playControls.locateVLC()
    if (int(VLCstartup)>=0):
        messageController.message("vlc found at " + VLCstartup,2)
    else:
        messageController.message("Error: Unable to locate vlc!",0)
        STARTUP = False
       
## main loop       
if(STARTUP):
    messageController.message("-- Main Loop --",2)
    messageController.message("Found the following media slots ...",2)
    timeslots = {}
    for slot in playlistController.getYaml():
        messageController.message(slot,2)
        slotTitle = list(slot)[0]
        slotAttributes = list(slot.values())[0]
        try:
            messageController.message(slotTitle + " @ " + slotAttributes['start'],2)
            timeslots[slotAttributes['start']] = slotTitle
        except KeyError:
            pass
    currentTick = 0
    while (currentTick < MAXTICK):
        messageController.message("-- Main Loop Tick --",2)
        timeNow = localtime()
        currentTimeString = str(timeNow.tm_hour).rjust(2, '0') + ":" + str(timeNow.tm_min).rjust(2, '0')
        if (str(timeNow.tm_min).rjust(2, '0') != MINUTEBUFFER):
            STARTUPMINUTE = False
        if(len(playControls.SWITCHOVER)>0):
            vlcStatus = str(playControls.getVlcStatus())
            if(vlcStatus == "Stopped"):
                messageController.message("Switchover! Starting stream!",1)
                playControls.playMedia({'stream': 'mopidy', 'uri': 'https://securestreams6.autopo.st:2222/stream'})
            messageController.message("VLC Status for switchover: " + vlcStatus,1)
        else:
            try:
                messageController.message("Trying for media ... " + "currentTimeString: " + currentTimeString,2)
                startMedia = timeslots[currentTimeString]
                slotToPlay = playlistController.getYaml()[playlistController.getPlaylistIndex(startMedia)]
                messageController.message(str(slotToPlay[startMedia]),2)
                if(not STARTUPMINUTE):
                    MINUTEBUFFER = str(timeNow.tm_min).rjust(2, '0')
                    playControls.playMedia(slotToPlay[startMedia])            
            except KeyError:
                # nothing to play so far, figure out if we need to recover and should already be playing
                messageController.message("DEBUG: looking for recovery timeslot",2)
                recoveryTimes = []
                timeDifferences = []
                for singleTimeslot in timeslots:
                    recoveryTimes.append(datetime.strptime(datetime.now().strftime("%m/%d/%Y") +" "+ singleTimeslot,"%m/%d/%Y %H:%M"))
                    timeDifferences.append(datetime.strptime(datetime.now().strftime("%m/%d/%Y") +" "+ singleTimeslot,"%m/%d/%Y %H:%M") - datetime.now())
                recoveryMode = False
                recoveryIndex = 0
                for timeDifference in enumerate(timeDifferences):
                    if(timeDifference[1].days < 0):
                        messageController.message("DEBUG: found a recovery slot",2)
                        recoveryMode = True
                        recoveryIndex = timeDifference[0]
                    else:
                        break
                if(recoveryMode and not playControls.PLAYBACK):
                    messageController.message("DEBUG: trying to recover at "+ str(recoveryIndex),2)
                    #use recoveryindex to get the start time of the concert
                    recoveryTimeString = recoveryTimes[recoveryIndex].strftime("%H:%M")
                    #access timeslots as usual
                    try:
                        messageController.message("Trying for media ... " + "Recovery timeslot: " + recoveryTimeString,2)
                        startMedia = timeslots[recoveryTimeString]
                        slotToPlay = playlistController.getYaml()[playlistController.getPlaylistIndex(startMedia)]
                        messageController.message(str(slotToPlay[startMedia]),2)
                        playControls.playMedia(slotToPlay[startMedia])            
                    except KeyError:
                        #print("DEBUG: didn't find a recovery slot")
                        # check if the first entry in yaml is a stream without start?
                        pass
                else:
                    firstEntry = list(playlistController.getYaml()[0].values())[0]
                    try:
                        if(firstEntry['stream'] == 'mopidy' and currentTick == 0):
                            messageController.message("First Entry is a stream!",2)
                            try:
                                testStartTime = firstEntry['start']
                            except KeyError:
                                playControls.playMedia(firstEntry)
                    except KeyError:
                        pass
                    messageController.message("Nothing to start!",1)
                        
        currentTick = currentTick + 1
        sleep(SLEEPTIME)


messageController.message("Dirigent v" + VERSION + " has shut down!",0)
