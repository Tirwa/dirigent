import subprocess
import distutils.spawn

class PlayControls:
    PLAYERCTL = ""
    PLAYBACK = False
    STARTUPMINUTE = False
    VLC = ""
    MOPIDY = ""    
    SWITCHOVER = []

    def __init__(self, messageHandler) -> None:
        self.messageController = messageHandler
        pass

    def playMedia(self, args):
        mediaFile = ''
        mediaStream = ''
        self.messageController.message("Stopping Playback ...",2)
        self.stopMedia()
        self.messageController.message("Trying to play " + str(args) + " ...",2)
        try:    #look for switchover
            switchoverFlag = args['switchover']
            if(switchoverFlag):
                self.SWITCHOVER = ['vlc', True]
            else:
                self.SWITCHOVER = []
        except KeyError:
            self.SWITCHOVER = []
        try:    #look for a file in the arguments
            mediaFile = args['file']
            self.messageController.message(mediaFile,2)
        except KeyError:
            self.messageController.message("No File in directions!",0)
        
        try:    # look for a stream in the arguments
            mediaStream = args['stream'] 
            self.messageController.message(mediaStream,2)
        except KeyError: 
            self.messageController.message("No Stream in directions!",0)
        
        if(mediaFile):
            self.playVlcFile(mediaFile)
            try:
                self.setVlcLoop(args['loopvideo'])
            except KeyError:
                self.setVlcLoop(False)

        if(mediaStream):
            streamUri = ''
            try:
                streamUri = args['uri']
            except KeyError:
                self.messageController.message("No URI found",0)
            self.messageController.message("Calling " + mediaStream + " now ...",2)
            if(streamUri):
                if(self.PLAYERCTL):
                    playerctlStartProcess = subprocess.run([self.PLAYERCTL, "-p", mediaStream, "open", streamUri])
            else:    
                if(self.PLAYERCTL):
                    playerctlStartProcess = subprocess.run([self.PLAYERCTL, "-p", mediaStream, "play"])

    def setVlcLoop(self, boolLoop):
        if(self.PLAYERCTL):
            if(boolLoop):
                playerctlVlcLoopInstructions = [self.PLAYERCTL, "-p", "vlc", "loop", "Track"]
            else:
                playerctlVlcLoopInstructions = [self.PLAYERCTL, "-p", "vlc", "loop", "None"]
            playerctlVlcLoopProcess = subprocess.run(playerctlVlcLoopInstructions)
    
    def stopMedia(self):
        if(self.PLAYERCTL):
            playertctlStopProcess = subprocess.run([self.PLAYERCTL, "-a", "pause"])

    def getVlcStatus(self):
        if(self.PLAYERCTL):
            playerctlVlcCheckProcess = subprocess.run([self.PLAYERCTL, "-p", "vlc", "status"], capture_output=True)
            playerctlVlcStdout = playerctlVlcCheckProcess.stdout.decode('UTF-8')[:-1].split(',')
            return str(playerctlVlcStdout[0])

    def playVlcFile(self, fileName):
        if(self.PLAYERCTL):
            playerctlVlcPlayInstructions = [self.PLAYERCTL, "-p", "vlc", "open", fileName]
            playerctlVlcPlayProcess = subprocess.run(playerctlVlcPlayInstructions)
            self.STARTUPMINUTE = True
            self.PLAYBACK = True

    def setupPlayerctl(self):
        self.PLAYERCTL = distutils.spawn.find_executable("playerctl")
        if (self.PLAYERCTL):
            self.messageController.message("playerctl found at " + self.PLAYERCTL, 2)
            self.messageController.message("Getting List of all available media players ...", 2)
            playerctlProcess = subprocess.run([self.PLAYERCTL, "--list-all"], capture_output=True)
            playerctlStdout = playerctlProcess.stdout.decode('UTF-8')[:-1].split(',')
            return playerctlStdout
        else:
            return -1
    
    def locateVLC(self):
        self.VLC = distutils.spawn.find_executable("vlc")
        if (self.VLC):
            return self.VLC
        else:
            return -1