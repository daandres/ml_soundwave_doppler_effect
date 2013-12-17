import properties.config as config
import os 
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
        
    
    def getGesture2D(self, recordClass, names=[], relativePathAdd=""):
        ''' get gesture as numpy 2D array '''
        # example: svm, tree

        lis = []
        for name in names:
            infile = relativePathAdd + config.gesturePath + "/" + name + GESTURE_PREFIX + str(recordClass) + FILE_END
            arr = np.loadtxt(infile, delimiter=",")
            lis.extend(arr.tolist())
        return np.array(lis)

    def getGesture3D(self, recordClass, names=[], relativePathAdd=""):
        ''' get gesture as numpy 3D array '''
        # example: markovmodel, lstm
        data2d = self.getGesture2D(recordClass, names, relativePathAdd)
        data3d = data2d.reshape((np.shape(data2d)[0], 32, 64))
        return data3d

if __name__ == "__main__":
#     np.set_printoptions(threshold=np.nan)
    g = GestureFileIO();
    data = g.getGesture3D(2, ["Daniel"])
    print data
    print np.shape(data)  
