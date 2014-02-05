import numpy as np
from gestureFileIO import GestureFileIO
#import config.config as c
np.set_printoptions(precision=2, linewidth=1000, threshold=5000)

class DataUtil:
    
    def __init__(self, lowerBound=0.15):
        self.lowerBound=lowerBound
        self.fileIO = GestureFileIO(relative="")

    def loadRaw3dGesture(self, recordClass, recordNames=['Daniel']):
        if recordNames is None:
            return self.fileIO.getGesture3D(recordClass)
        else:
            return self.fileIO.getGesture3D(recordClass, recordNames)

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

    def normalize(self, data):
        ''' normalizes date between 0 and 1 '''
        
        result = []
        for i in data:
            aMax = np.amax(i)
            result.append(i/aMax)
        return np.array(result)
    
    def loadRaw3DArray(self, path=["data/gesture_0.txt"]):
        ''' get gesture as numpy 3D array '''
        
        data3d = []
        for p in path:
            #p = "../" + p
            data2d = self._loadRaw2DArray(p)
            data3d.extend(self._convert2dTo3d(data2d))
        return np.array(data3d)
    
    def splitData(self, data):
        ''' splits data in 2/3 training, 1/3 test '''
        
        train, test = list(data[::3]) + list(data[1::3]), data[2::3]
        return np.array(train), test
    
        
    def reduceBins(self, data, leftBorder=26, rightBorder=39):
        ''' reduces array from 64 to 16 bins '''

        data3dNew = np.zeros((data.shape[0], data.shape[1], rightBorder-leftBorder))

        # use only the next 8 bins from the peak middle to left and right
        for d in range(len(data)):
            for dd in range(len(data[d])):
                data3dNew[d][dd] = data[d][dd][leftBorder:rightBorder]
        return data3dNew
    
    def normalizeBound(self, data, lowerBound=0.15, upperBound=None):
        '''
        Uses normalized data and sets values under lowerBound to 0 
        and if set, above upperBound to 1
        '''
        
        result = np.where(data[:,:,:]<lowerBound, 0.0, data[:,:,:])
            
        if upperBound is not None:
            result = np.where(result[:,:,:] > self.upperBound, 1.0, result[:,:,:])
        
        return result

    def normalizeBounds(self, data):
        '''
        Uses normalized data and sets values under lowerBound to 0
        and above upperBound to 1
        '''
        lis = []
        # gesture
        for e in data:
            maxi = np.max(e)
            x = e / (maxi*1.0)
            x = np.where(x[:,:]<self.lowerBound, 0, x[:,:])
            if np.count_nonzero(x) > 59:
                x = x * 700
                lis.append(x)

        return np.array(lis)
    
    def cutRelevantAction(self,data, framesBefore=6, framesAfter=6):
        ''' 
        extracts relevant actions from data 
        
        '''
        
        frameRange = framesBefore + framesAfter +1
        if frameRange > np.shape(data)[1]:
            return data
        result = np.zeros((np.shape(data)[0], frameRange, np.shape(data)[2]))
        i=0
        for d in data:
            pos = self._getHighestSum(d)
            indexBegin = 0
            indexEnd = 0
            fitting = 0
            if(pos-framesBefore)<0:
                fitting = abs(pos-framesBefore)
            else:
                indexBegin = pos-framesBefore
            if(pos + framesAfter) > (np.shape(d)[0]-1):
                indexEnd = np.shape(d)[0]
                fitting = fitting + (pos + framesAfter - (np.shape(d)[0]-1))
            else:
                indexEnd =  pos + framesAfter+1
            resultTmp = d[indexBegin:indexEnd]
            if fitting > 0:
                zeros = np.zeros((fitting, np.shape(data)[2]))
                resultTmp = np.append(resultTmp,zeros)
                resultTmp = resultTmp.reshape((frameRange,np.shape(data)[2]))
            result[i] = resultTmp
            i+=1
        return result
        
    def _getHighestSum(self, gesture):
        highestValue = 0
        position = 0
        
        for i in range(len(gesture)):
            highTmp = np.sum(gesture[i])
            if highTmp > highestValue:
                highestValue = highTmp
                position = i
        return position
    

    def findAvg(self, data):

        summe = []
        
        for gesture in data:
            for frame in gesture:
                su = np.sum(frame)
                summe.append(su)
        return np.average(np.array(summe))

    def show(self, data):
        for i in data:
            for j in i:
                print str(j) + " " + str(np.sum(j))
            print "new Gesture"

    def fillArray(self, data):
        ''' fills data back to 64 bins for printing with bob_visualizer_2 '''
        
        result = np.zeros((np.shape(data)[0], 32, 64))
        for i, gesture in enumerate(data):
            for j, frame in enumerate(gesture):
                result[i,j, :len(frame)] = frame
        return result

    def cutPeak(self, data):
        '''
        cuts peak signal for gesture
        '''
        l = len(data[0][0]) / 2
        leftBound = l - 1
        rightBound = l + 2
        for i, gesture in enumerate(data):
            for j, frame in enumerate(gesture):
                data[i, j, leftBound:rightBound] = 0.0
        return data

    def round(self, data):
        return np.round(data, 1)

    def cutBad(self, data):
        avgLis = []
        for gesture in data:
            avgLis.append(np.count_nonzero(gesture))
        avg = np.average(avgLis)
        
        result = []
        for gesture in data:
            if np.count_nonzero(gesture) > avg-(0.05 * avg):
                result.append(gesture)
        return np.array(result)
        

if __name__ == "__main__":
    print "#### START ####"
    dp = DataUtil()
    path=["../data/clean.txt"]
    
    data = dp.loadRaw3dGesture(0)
    data = dp.reduceBins(data)
    data = dp.normalize(data)
    data = dp.normalizeBound(data)
    data = dp.cutRelevantAction(data)
    dp.cutBad(data)
    
#     y = dp.fillArray(data)
#     y = dp.normalizeBounds(y)
#     y = dp._convert3dTo2d(y)
# 
#     np.savetxt("../data/formated.txt", y, fmt='%1.2f', delimiter=",")

    print "#### END ####"