import numpy as np
from gestureFileIO import GestureFileIO
import classifier.hmm.config.config as c

class DataUtil:
    ''' Class for loading and preprocessing gesture-data '''
    
    def __init__(self):
        self.fileIO = GestureFileIO(relative="")

    def loadRaw3dGesture(self, recordClass, recordNames=None):
        ''' loads raw data from the gesture dir '''
        if recordNames is None:
            return self.fileIO.getGesture3D(recordClass, c.names)
        else:
            return self.fileIO.getGesture3D(recordClass, recordNames)


    def _reduceBins(self, data, leftBorder=c.leftBorder, rightBorder=c.rightBorder+1):
        ''' reduces array from 64 to 16 bins '''
        return data[:, :, leftBorder:rightBorder]

    def _amplifyFunction(self, x):
        return x * (2.8 * ( x - 1.15 )**2 + 0.75)

    def _normalize(self, data):
        ''' normalizes gesture between 0 and 1 '''
        
        result = []
        for gesture in data:
            aMax = np.amax(gesture)
            result.append(gesture/aMax)
        return np.array(result)
    
    def splitData(self, data):
        ''' splits data in 3/4 training, 1/4 test '''
        
        train, test = list(data[::4]) + list(data[1::4]) + list(data[2::4]), data[3::4]
        return np.array(train), test
    
    def _cutThresholdAndAmplify(self, data, lowerBound=0.15):
        '''
        Sets values under lowerBound to 0
        and amplifiy / reduce values
        (uses normalized data)
        '''
        
        result = np.where(data[:,:,:]<lowerBound, 0.0, self._amplifyFunction(data[:,:,:]))
        return result


    def preprocessData(self, data):
        ''' public method to send data through the preproc pipeline'''

        data = self._reduceBins(data)
        data = self._normalize(data)
        data = self._cutThresholdAndAmplify(data)
        data = np.round(data, 1)
        return data

    def loadData(self, gesture):
        ''' public method to load preproc data '''
        data= self.loadRaw3dGesture(gesture)
        data = self.preprocessData(data)
        return data

    def loadSplitData(self, gesture):
        ''' public method to load splitted preproc data '''
        data = self.loadData(gesture)
        return self.splitData(data)

    def _getHighestSum(self, gesture):
        highestValue = 0
        position = 0
        
        for i in range(len(gesture)):
            highTmp = np.sum(gesture[i])
            if highTmp > highestValue:
                highestValue = highTmp
                position = i
        return position
        '''
        for i in range(len(gesture)):
            ab = np.abs(gesture[i])
            highTmp = np.sum(ab)
            if highTmp > highestValue:
                highestValue = highTmp
                position = i
        return position
        '''
