from threading import Thread, enumerate
from view.console import Console
from view.visualizer import View
from soundplayer import Sound
from recorder import SwhRecorder
import properties.config as config
from gestureFileIO import GestureFileIO
import thread

import os
import sys 
     
class SenseGesture():
    
    def __init__(self):
        self._setConfig()
        self.soundPlayer = Sound()

        self.gestureFileIO = GestureFileIO()
        self.recorder = SwhRecorder(self.gestureFileIO, self.frequency)
        
        self.view = Console(self.recorder, self.applicationClose)
        
        self.t1 = None
        self.t2 = None
        self.t3 = None
        

    def _setConfig(self):
        self.checkNameSet()

        self.frequency = config.frequency
        self.amplitude = config.amplitude
        self.framerate = config.framerate
        self.duration = config.duration
        self.path = config.gesturePath

    def checkNameSet(self):
        if(config.name == ""):
            name = raw_input('Bitte schreibe deinen Namen:\n')
            outfile = "properties/personal.py"
            oid = open(outfile, "w")
            data = "name=\"" + name + "\""
            oid.write(data)
            oid.close()
            self.name = name
            # TODO reload config file properly instead of exiting programm
            sys.exit(0)
        else:
            self.name = config.name
        
        

    def start(self):
        try:
            self.t1 = Thread(name="Soundplayer", target=self.soundPlayer.startPlaying, args=(self.frequency, self.amplitude, self.framerate, self.duration))
            self.t2 = self.recorder.startNewThread()
            self.t3 = self.view.startNewThread()
            self.t1.start()
        except:
            print "Error: unable to start thread ", sys.exc_info()
    
    def applicationClose(self, code=0):
        self.recorder.close()
        # TODO Close Player clean 
        self.soundPlayer.stopPlaying()
        print "Player alive: " + str(self.t1.is_alive())
        print "Recorder alive: " + str(self.recorder.is_alive())
        print "View alive: " + str(self.view.is_alive())
        print enumerate()
        thread.interrupt_main()
        
        
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
    try:
        print("Started Gesture Recognition")
        app = SenseGesture()
        # app.deleteGestures()
        app.start()
    except KeyboardInterrupt:
        print "Exit"