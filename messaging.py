class Messaging:
    DEBUG = False
    def __init__(self, debug):
        self.DEBUG = debug

    def message(self, messageText, messageType=0): #0: ERROR, 1: WARN, 2: DEBUG/INFO
        outputString = str(messageText)
        if self.DEBUG:
            print(outputString)
        elif messageType == 0:
            print(outputString)        
