from threading import Thread, enumerate
from view.console import Console, printHelp
from soundplayer import Sound
from recorder import SwhRecorder
import properties.config as c
from gestureFileIO import GestureFileIO
import sys

class SenseGesture():

    def __init__(self):
        print("Started Gesture Recognition")
        self._setConfig()
        self.soundPlayer = Sound()

        self.gestureFileIO = GestureFileIO(self.name, self.path)
        self.recorder = SwhRecorder(self.gestureFileIO, self.audioConfig, self.recordConfig)

        self.view = Console(self.recorder, self.applicationClose, self.gestureFileIO.setFileName, self.gestureFileIO.getFileName)

        self.t1 = None
        self.t2 = None
        self.t3 = None


    def _setConfig(self):
        self.config = c.getInstance()
        self.checkNameSet()

        self.audioConfig = self.config.getAudioConfig()
        self.pathsConfig = self.config.getPathsConfig()
        self.recordConfig = self.config.getRecordConfig()

        self.frequency = float(self.audioConfig['frequency'])
        self.amplitude = float(self.audioConfig['amplitude'])
        self.framerate = int(self.audioConfig['framerate'])
        self.duration = int(self.audioConfig['duration'])
        self.bufsize = int(self.audioConfig['buffersize'])
        self.path = self.pathsConfig['gesturepath']

    def checkNameSet(self):
        userconfig = self.config.getUserConfig()
        if(userconfig['name'] == ""):
            name = raw_input('Bitte schreibe deinen Namen:\n')
            self.config.setConfig("user", "name", name)
            self.name = name
        else:
            self.name = userconfig['name']



    def start(self):
        try:
            self.t1 = Thread(name="Soundplayer", target=self.soundPlayer.startPlaying, args=(self.frequency, self.amplitude, self.framerate, self.duration, self.bufsize))
            self.t2 = self.recorder.startNewThread()
            self.t3 = self.view.startNewThread()
            self.t1.start()
        except:
            print("Error: unable to start thread ", sys.exc_info())
        self.t3.join()
#         self.applicationClose()
        print("Player alive: \t" + str(self.t1.is_alive()))
        print("Recorder alive:\t" + str(self.recorder.is_alive()))
        print("View alive: \t" + str(self.view.is_alive()))
        exitApp()

    def applicationClose(self, code=0):
        self.recorder.close()
        self.soundPlayer.stopPlaying()

        self.recorder.thread.join()
        self.t1.join()

def exitApp():
    print(enumerate())
    print("Exit")
    sys.exit(0)

if __name__ == '__main__':
    try:
#         printHelp()
        app = SenseGesture()
        app.start()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        exitApp()
