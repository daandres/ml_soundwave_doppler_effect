from threading import Thread
import realTimeAudio as r
from soundplayer import Sound
t1 = None
t2 = None

def main():
    soundPlayer = Sound()
    frequency = 21000.0
    amplitude = 0.5
    framerate = 48100
    duration = 600
    try:
        t1 = Thread(target=soundPlayer.playSound, args=(frequency, amplitude, framerate, duration))
        t2 = Thread(target=r.init, args=())
        t1.start()
        t2.start()
    except:
        print("Error: unable to start thread")
    
    while t2.is_alive():
        pass
    else:
        print("Finished")

if __name__ == '__main__':
    print("Me started")
    main()
    print("Exit")
#     sys.exit()