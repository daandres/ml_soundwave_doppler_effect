from threading import Thread
import realTimeAudio as r
from soundplayer import *
runtime = 60
t1 = None
t2 = None

def main():
    
    try:
        t1 = Thread(target=playsound, args=(21000.0, 0.5, 48100, 600))
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
    sys.exit()