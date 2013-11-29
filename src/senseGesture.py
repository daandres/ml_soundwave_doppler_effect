from threading import Thread
from realTimeAudio import View
from soundplayer import Sound
import properties.config as config
import os 
     
class SenseGesture():
    
    def __init__(self):
        self._setConfig()
        self.soundPlayer = Sound()
        self.view = View(self.frequency, self.fRange)
        
        self.t1 = None
        self.t2 = None
        
        if not os.path.exists(config.gesture_path):
            os.makedirs(config.gesture_path)

    def _setConfig(self):
        self.frequency = config.frequency
        self.fRange = config.fRange
        self.amplitude = config.amplitude
        self.framerate = config.framerate
        self.duration = config.duration
        self.path = config.gesture_path

    def start(self):
        
        try:
            self.t1 = Thread(target=self.soundPlayer.playSound, args=(self.frequency, self.amplitude, self.framerate, self.duration))
            self.t2 = Thread(target=self.view.start, args=())
            self.t1.start()
            self.t2.start()
        except:
            print("Error: unable to start thread")
        
        while self.t2.is_alive():
            pass
        else:
            self.soundPlayer.stopSound()
            
    def deleteGestures(self):
        folder = config.gesture_path
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