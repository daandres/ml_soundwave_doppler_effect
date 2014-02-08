import numpy as np
from gestureFileIO import GestureFileIO
import classifier.hmm.config.config as c

class DataUtil:
    
    def __init__(self, lowerBound=0.15):
        self.lowerBound=lowerBound
        self.fileIO = GestureFileIO(relative="")

    def _loadRaw2DArray(self, path="data/gesture_0.txt"):
        ''' get gesture as numpy 2D array '''
    
        data2d = np.loadtxt(path, delimiter=",")
        return data2d
    
    def _convert2dTo3d(self, data2d):
        ''' converts 2d gesture data to 3d gesture data'''
        
        data3d = data2d.reshape((np.shape(data2d)[0], 32, 64))
        return data3d

    def _convert3dTo2d(self, data):
        
        data2d = []
        for gesture in data:
            data2d.append(np.ravel(gesture))
        return np.array(data2d)

    def loadRaw3dGesture(self, recordClass, recordNames=None):
        if recordNames is None:
            return self.fileIO.getGesture3D(recordClass, ["paul"]) # insert names here
        else:
            return self.fileIO.getGesture3D(recordClass, recordNames)

    def reduceBins(self, data, leftBorder=c.leftBorder, rightBorder=c.rightBorder+1):
        ''' reduces array from 64 to 16 bins '''
        return data[:, :, leftBorder:rightBorder]
    
#         data3dNew = np.zeros((data.shape[0], data.shape[1], rightBorder-leftBorder))
# 
#         # use only the next 8 bins from the peak middle to left and right
#         for d in range(len(data)):
#             for dd in range(len(data[d])):
#                 data3dNew[d][dd] = data[d][dd][leftBorder:rightBorder]
#         return data3dNew

    def normalize(self, data):
        ''' normalizes gesture between 0 and 1 '''
        
        result = []
        for gesture in data:
            aMax = np.amax(gesture)
            result.append(gesture/aMax)
        return np.array(result)
    
    def splitData(self, data):
        ''' splits data in 2/3 training, 1/3 test '''
        
        train, test = list(data[::4]) + list(data[1::4]) + list(data[2::4]), data[3::4]
        return train, test
    
    def cutThreshold(self, data, lowerBound=0.15, upperBound=None):
        '''
        Uses normalized data and sets values under lowerBound to 0 
        and if set, above upperBound to 1
        '''
        
        result = np.where(data[:,:,:]<lowerBound, 0.0, data[:,:,:])
        return result
    
    def cutRelevantAction(self,data, framesBefore=c.framesBefore, framesAfter=c.framesAfter):
        ''' 
        extracts relevant actions from data 
        
        '''
        
        frameRange = framesBefore + framesAfter +1
        if frameRange > np.shape(data)[1]:
            return data
        # Old Version. Fills not completed Actions with zeros
        '''
        result = np.zeros((np.shape(data)[0], frameRange, np.shape(data)[2]))
        i=0
        for d in data:
            pos = self._getHighestSum(d)
            indexBegin = 0
            indexEnd = 0
            fittingBefore = 0
            fittingAfter = 0
            if(pos-framesBefore)<0:
                fittingBefore = abs(pos-framesBefore)
            else:
                indexBegin = pos-framesBefore
            if(pos + framesAfter) > (np.shape(d)[0]-1):
                indexEnd = np.shape(d)[0]
                fittingAfter = (pos + framesAfter - (np.shape(d)[0]-1))
            else:
                indexEnd =  pos + framesAfter+1
            if fittingBefore > 0:
                break
                zeros = np.ones((fittingBefore, np.shape(data)[2]))
                zeros = zeros*0.001
                resultTmp = resultTmp = np.append(zeros,d[indexBegin:indexEnd])
                resultTmp = resultTmp.reshape((indexEnd-indexBegin+fittingBefore,np.shape(data)[2]))
            else:
                resultTmp = d[indexBegin:indexEnd]
            if fittingAfter > 0:
                break
                zeros = np.ones((fittingAfter, np.shape(data)[2]))
                zeros = zeros*0.001
                resultTmp = np.append(resultTmp,zeros)
                resultTmp = resultTmp.reshape((frameRange,np.shape(data)[2]))
            result[i] = resultTmp
            i+=1
        return result
        '''
        # New Version - Revert none completed actions
        result = np.zeros((np.shape(data)[0], frameRange, np.shape(data)[2]))
        i = 0
        #print np.shape(data)
        for j, d in enumerate(data):
            # subtract no gesture mean values from data
            #d = d - np.array([2.52e-05,2.37e-05,1.06e-04,1.34e-03,2.13e-01,4.60e-01,9.83e-01,8.19e-01,2.57e-01,1.57e-01,1.98e-04,5.28e-05,2.47e-05])
            pos = self._getHighestSum(d)
            if((pos-framesBefore)<0) | ((pos + framesAfter) > (np.shape(d)[0]-1)):
                #print j+1
                continue
            indexBegin = pos-framesBefore
            indexEnd =  pos + framesAfter+1
            #print gest
            result[i] = self.amplifySignal(d[indexBegin:indexEnd])
            i += 1
        #print np.shape(result[0:i])
        return result[0:i]

    def amplifyFunction(self, x):
        return x * (3 * ( x - 1 )**2 + 0.75)

    def amplifySignal(self, gesture):
        l = [self.amplifyFunction(x) for x in gesture]
        return np.array(l)
       
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

    def round(self, data):
        return np.round(data, 1)

    def preprocessData(self, data):
        data = self.reduceBins(data)
        data = self.normalize(data)
        data = self.cutThreshold(data)
        data = self.cutRelevantAction(data)
        data = self.round(data)
        return data

    def loadData(self, gesture):
        data= self.loadRaw3dGesture(gesture)
        data = self.preprocessData(data)
        return data

    def loadSplitData(self, gesture):
        data = self.loadData(gesture)
        return self.splitData(data)
