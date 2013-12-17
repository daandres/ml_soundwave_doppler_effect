from threading import Thread
from realTimeAudio import View
from soundplayer import Sound
from recorder import SwhRecorder
import properties.config as config
import os 
import sys

import numpy as np

FILE_END = ".txt"
GESTURE_PREFIX = "/gesture_"
     
class GestureFileIO():
    

    def __init__(self):
        self.name = config.name
        namedPath = config.gesturePath + "/" + self.name
        if not os.path.exists(namedPath):
            os.makedirs(namedPath)
        
        
    def writeGesture(self, recordClass, recordData):
        ''' adds the give gesture to the personal gesture file ''' 
        outfile = config.gesturePath + "/" + self.name + GESTURE_PREFIX + str(recordClass) + FILE_END
        print outfile
        oid = open(outfile, "a")
        # oid.write("##### Class " + str(self.recordClass) + " #####\n")
        # flatten all inputs to 1 vector
        data = np.array([np.array(np.ravel(recordData))])
        print "Wrote record for class " + str(recordClass)
        np.savetxt(oid, data, delimiter=",", fmt='%1.4f')
        oid.close()
        
    
    def getGesture2D(self, recordClass, names=[]):
        ''' get gesture as numpy 2D array '''
        # example: svm, tree

        lis = []
        for name in names:
            infile = config.gesturePath + "/" + name + GESTURE_PREFIX + str(recordClass) + FILE_END
            arr = np.loadtxt(infile, delimiter=",")
            lis.extend(arr.tolist())
        return np.array(lis)

    def getGesture3D(self, recordClass, names=[]):
        ''' get gesture as numpy 3D array '''
        # example: markovmodel
        return

if __name__ == "__main__":
    g = GestureFileIO();
    print g.getGesture2D(2, ["ppasler"])
        