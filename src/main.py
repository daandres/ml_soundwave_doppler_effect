from threading import Thread
from realTimeAudio import View
from soundplayer import Sound
import sys
t1 = None
t2 = None

def main():
    soundPlayer = Sound()
    view = View()
    frequency = 21000.0
    amplitude = 0.5
    framerate = 48100
    duration = 600
    try:
        t1 = Thread(target=soundPlayer.playSound, args=(frequency, amplitude, framerate, duration))
        t2 = Thread(target=view.start, args=())
        t1.start()
        t2.start()
    except:
        print("Error: unable to start thread")
    
    while t2.is_alive():
        pass
    else:
        soundPlayer.stopSound()


if __name__ == '__main__':
    print("Started Gesture Recognition")
    main()
    print("Exit")
    sys.exit()