import os
import numpy as np
import pandas as pd
import time

FILE_END = ".txt"
GESTURE_PREFIX = "/gesture_"

class GestureFileIO():

    def __init__(self, name="", gesturePath="../gesture"):
        self.name = name
        self.basePath = gesturePath
        self.namedPath = gesturePath + "/" + self.name

        if not os.path.exists(self.namedPath):
            os.makedirs(self.namedPath)
        for i in range(8):
            outdir = self.namedPath + GESTURE_PREFIX + str(i) + "/"
            if not os.path.isdir(outdir):
                os.mkdir(outdir)
        self.filenamebase = str(time.time())[:-3]

    def writeGesture(self, recordClass, recordData):
        ''' adds the give gesture to the personal gesture file '''
        outfile = self.getFileName(recordClass)
        oid = open(outfile, "a")
        # flatten all inputs to 1 vector
        data = np.array([np.array(np.ravel(recordData))])
#         print "Wrote record for class " + str(recordClass)
        np.savetxt(oid, data, delimiter=",", fmt='%1.4f')
        oid.close()


    def getGesture2D(self, recordClass, names=[], relativePathAdd=""):
        ''' get gesture as numpy 2D array '''
        # example: svm, tree
        if len(names) == 0:
            for folder in os.walk(relativePathAdd + self.basePath):
                names = folder[1]
                print names
                break
        completearray = None
        for name in names:
            indir = relativePathAdd + self.basePath + "/" + name + GESTURE_PREFIX + str(recordClass) + "/"
            for infile in os.listdir(indir):
                if infile.endswith(FILE_END):
                    arr = pd.read_csv(indir + infile, sep=',', header=None)
                    arr = np.asarray(arr)
                    if completearray is None:
                        completearray = arr
                    else:
                        completearray = np.append(completearray, arr, axis=0)
        if completearray is None:
            completearray = np.zeros((1, 2048))
        return completearray
#         lis = []
#         for name in names:
#             infile = relativePathAdd + config.gesturePath + "/" + name + GESTURE_PREFIX + str(recordClass) + FILE_END
#             arr = np.loadtxt(infile, delimiter=",")
#             lis.extend(arr.tolist())
#         return np.array(lis)

    def getGesture3D(self, recordClass, names=[], relativePathAdd=""):
        ''' get gesture as numpy 3D array '''
        # example: markovmodel, lstm
        data2d = self.getGesture2D(recordClass, names, relativePathAdd)
        data3d = data2d.reshape((np.shape(data2d)[0], 32, 64))
        return data3d

    def setFileName(self, name):
        self.filenamebase = str(name)

    def getFileName(self, recordClass):
        outdir = self.namedPath + GESTURE_PREFIX + str(recordClass) + "/"
        outfile = outdir + self.filenamebase + FILE_END
        return outfile

if __name__ == "__main__":
#     np.set_printoptions(threshold=np.nan)
    g = GestureFileIO("Daniel", "../gesture");
    data = g.getGesture3D(1, [])
    print data
    print np.shape(data)
