from threading import Thread
import realTimeAudio as r
from soundplayer import *


def main():
    try:
        t1 = Thread(target=playsound, args=(21000.0, 0.5, 48100, 30))
        t2 = Thread(target=r.init, args=())
        t1.start()
        t2.start()
    except:
       print("Error: unable to start thread")
    
    while True:
        pass


if __name__ == '__main__':
    print("Me started")
    main()