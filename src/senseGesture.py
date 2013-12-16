from threading import Thread
from realTimeAudio import View
from soundplayer import Sound
from recorder import SwhRecorder
import properties.config as config
import os 
import sys
     
class SenseGesture():
    
    def __init__(self):
        self._setConfig()
        self.soundPlayer = Sound()

        self.recorder = SwhRecorder(self.frequency)
        
        self.view = View(self.recorder)
        
        self.t1 = None
        self.t2 = None
        self.t3 = None
        

    def _setConfig(self):
        self.checkNameSet()

        self.frequency = config.frequency
        self.fRange = config.fRange
        self.amplitude = config.amplitude
        self.framerate = config.framerate
        self.duration = config.duration
        self.path = config.gesturePath

    def checkNameSet(self):
        if(config.name==""):
            name = raw_input('Bitte schreibe deinen Namen:\n')
            outfile = "properties/personal.py"
            oid = open(outfile, "w")
            data = "name=\"" + name + "\""
            oid.write(data)
            oid.close()
            self.name=name
            # TODO reload config file properly instead of exiting programm
            sys.exit(0)
        else:
            self.name = config.name
        
        namedPath = config.gesturePath + "/" + self.name
        if not os.path.exists(namedPath):
            os.makedirs(namedPath)

    def start(self):
        try:
            self.t1 = Thread(target=self.soundPlayer.startPlaying, args=(self.frequency, self.amplitude, self.framerate, self.duration))
            self.t2 = Thread(target=self.recorder.record, args=())
            self.t3 = Thread(target=self.view.start, args=())
            self.t1.start()
            self.t2.start()
            self.t3.start()
        except:
            print("Error: unable to start thread")
        
        while self.t3.is_alive():
            pass
        else:
            self.recorder.stopRecording()
            #TODO Close Player clean 
            self.soundPlayer.stopPlaying()
            
        print "Player alive: " + str(self.t1.is_alive())
        print "Recorder alive: " + str(self.t2.is_alive())
        print "View alive: " + str(self.t3.is_alive())
            
    def deleteGestures(self):
        folder = config.gesturePath
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e


if __name__ == '__main__':
    print("Started Gesture Recognition")
    app = SenseGesture()
    #app.deleteGestures()
    app.start()
    print("Exit")
#     sys.exit()