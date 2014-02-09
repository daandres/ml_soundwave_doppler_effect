import copy
import numpy as np
from scipy import stats
from sklearn import cluster

class kMeansHepler():

        #check one gesture after segmentation
        #return the amount of similar class   
    def checkKMeansForSegmentation(self, learnArray, k=2, maxItKMeans=5, loopCount=10):
        kmeans = cluster.KMeans(k,  max_iter=maxItKMeans)
        resultCount = 0
        for x in xrange(loopCount):
            cluster_ = kmeans.fit_predict(learnArray)
            mode, count = stats.mode(cluster_)
            if mode.shape[0] > 1: continue
            if count > resultCount:
                resultCount = count
        return int((float(resultCount)/float(learnArray.shape[0]))*100), cluster_, mode, kmeans
           
            
        #http://stackoverflow.com/questions/17907614/finding-local-maxima-of-xy-data-point-graph-with-numpy
        #get local maximum of a function
    def localMaxima(self, xval, yval):
        xval = np.asarray(xval)
        yval = np.asarray(yval)
    
        sort_idx = np.argsort(xval)
        yval = yval[sort_idx]
        gradient = np.diff(yval)
        maxima = np.diff((gradient > 0).view(np.int8))
        return np.concatenate((([0],) if gradient[0] < 0 else ()) +
                              (np.where(maxima == -1)[0] + 1,) +
                              (([len(yval)-1],) if gradient[-1] > 0 else ()))    
        
        
        #lock for the local maximum (besides the amplitude) and compare it by all frames
        #chose the highest local maximum as the middle of a gesture 
        #return a array with length = outArrayLength  
    def segmentOneHandGesture(self, inArray, outArrayLength=16, leftMargin=3, oneSecPeak=True):
        
        globalRatio = 0.0
        matchFrameIdx = 0
        resultArray = None
        globalMax = np.amax(inArray)
        firstRightPeak = True
        ratio = 0
        for idx, frame in enumerate(inArray):
            
            maxV = np.amax(frame)
            xDummies = a = np.arange(len(frame))
            frAsArray =  np.asanyarray(frame)
            #get local max
            lMaxIdx =  self.localMaxima(xDummies, frame)
            #get values at local max
            lMaxVal = frAsArray[lMaxIdx]
            #get sorted indices of the local max
            lMaxIdxSort = lMaxVal.argsort()[-3:][::-1]
            #calculate ratio global / first local max
            
            if lMaxVal.shape[0]>2:
                ratio = lMaxVal[lMaxIdxSort[1]]/lMaxVal[lMaxIdxSort[0]]
                #check if the local max is at first right to the global max => recognize gesture 3
                isRightPeak =  lMaxIdxSort[1] > lMaxIdxSort[0]
                if not oneSecPeak:
                    if not isRightPeak and ratio > 0.1 :
                        firstRightPeak = False
            if ratio > globalRatio and maxV/ globalMax > 0.7 and firstRightPeak:
                globalRatio = ratio       
                matchFrameIdx = idx
                
        leftIdx = matchFrameIdx - leftMargin
        rightIdx = matchFrameIdx + outArrayLength - leftMargin         
        if leftIdx >= 0 and rightIdx < inArray.shape[0] :
            resultArray = inArray[leftIdx:rightIdx]
            resultArray = np.asanyarray(resultArray)
        
        return resultArray


        #helper function to reshape a 2D array to a 3D
    def reshapeArray2DTo3D64(self, inArray2D):
        frames = inArray2D.shape[1]/64
        return inArray2D.reshape(inArray2D.shape[0], frames, 64) 
         
         
        #helper function to reshape a 3D array to a 2D         
    def reshapeArray3DTo2D64(self, inArray3D):
        return inArray3D.reshape(inArray3D.shape[0], inArray3D.shape[1]*inArray3D.shape[2],) 
    
    
        #check the gesture distance to the nearest and the second one
        #if the distance ratio is higher than perRatio return closest centorids
        #otherwise return -1 
    def checkClusterDistance(self, disToCentre, perRatio=10):
        sortedDistance = np.argsort(disToCentre[0])
        distanceRatio = disToCentre[0][sortedDistance[1]]/disToCentre[0][sortedDistance[0]]  
        if distanceRatio > 1. + perRatio/100.:
            return sortedDistance[0]
        else:
            return -1   
    
    
        #is a try to segment a two hands gesture
        #the difficulty by that is that this gesture has more than one local maximum 
        #is capable of improvement
    def segmnetTwoHandsGesture(self, inArray, outArrayLength=16, leftMargin=3):
        resultArray = None
        matchFrameIdx = 0
        bestRatioArray = []
        peak3Over = False
        peak3frameReached = False
        
        for idx, frame in enumerate(inArray):
            
            frame_ = frame[16:(len(frame)-16)]
            print frame_.shape
            maxV = np.amax(frame_)
            xDummies = a = np.arange(len(frame_))
            frAsArray =  np.asanyarray(frame_)
            #get local max
            lMaxIdx =  self.localMaxima(xDummies, frame_)
            if len(lMaxIdx) < 3:
                print '3 peaks not here ;-)'
                peak3frameReached = True
                continue
            #get values at local max
            lMaxVal = frAsArray[lMaxIdx]
            #get sorted indices of the local max
            lMaxIdxSort = lMaxVal.argsort()[-3:][::-1]       
            #the highest local max is left to global max
            localMaxLeft = (lMaxIdxSort[2] > lMaxIdxSort[0] and lMaxIdxSort[1] < lMaxIdxSort[0])
            #the highest local max is right to global max
            localMaxRight = (lMaxIdxSort[1] > lMaxIdxSort[0] and lMaxIdxSort[2] < lMaxIdxSort[0])
            #first two local max are left and right to the global max
            isThreePeakFrame = localMaxLeft or localMaxRight 
            if isThreePeakFrame and not peak3Over:
                #if local max higher than 10% of global max
                if lMaxVal[lMaxIdxSort[1]] > maxV*0.1 and lMaxVal[lMaxIdxSort[2]] > maxV*0.1 :
                    peak3frameReached = True
                    bestRatioArray.append([lMaxVal[lMaxIdxSort[2]]/lMaxVal[lMaxIdxSort[1]], idx])
                #if local max level smaller than 10% of global max and the first part of the two hands gesture is over        
                elif peak3frameReached:
                    bestRatioArray = np.asarray(bestRatioArray)
                    if bestRatioArray.shape[0] > 1:
                        minIdx = np.argmin(bestRatioArray[::,0:1])
                        matchFrameIdx = bestRatioArray[minIdx][1]
                    #print 'matchFrameIdx : ', matchFrameIdx  
                    peak3Over = True
                
        leftIdx = matchFrameIdx - leftMargin
        rightIdx = matchFrameIdx + outArrayLength - leftMargin         
        if leftIdx >= 0 and rightIdx < inArray.shape[0] :
            resultArray = inArray[leftIdx:rightIdx]
            resultArray = np.asanyarray(resultArray)
        
        return resultArray


        #normalize values of the 1D input array
    def normalizeSignalLevelSecond(self, frame, newMaxV=800, gradLevel=10, grad=False):
        maxP = np.argmax(frame)
        maxV = np.amax(frame)
        result = copy.copy(frame)       
        for x in xrange(len(frame)):
            if grad:
                result[x] = (float(int((frame[x] / maxV)*gradLevel)))/gradLevel*newMaxV
            else:
                result[x] = (frame[x] / maxV) * newMaxV
        result[maxP] = newMaxV
        
        return result
    
    
        #normalize values of the 2D input array
    def normalize3DArray(self, inArray3D):
        result = []
        for gesture in inArray3D:
            gestureTMP = []
            for frame in gesture:
                gestureTMP.append(self.normalizeSignalLevelSecond(frame))
            result.append(gestureTMP)
            
        return np.asarray(result)
    
    
        #cut the values of the 64 peaks which are not relevant for the classification
        #the best value for that seem to be 24, in the next two steps we reduce the dimensionality
        #by calculating the average of two neighbors frames. After that we get a 6 x 12 shape
        #and return that linear combination   
    def reduceDimensionality(self, inArray, sidesCut=24, manyTimes=4, setAxisTo=0, std='cut'):
        

        if std=='cut':
            sidesCutedArray = inArray[:,sidesCut:(inArray.shape[1]-sidesCut)]
            result = []
            for x in xrange(0,sidesCutedArray.shape[0]-1,2):
                arrTMP = []
                arrTMP.append(sidesCutedArray[x])
                arrTMP.append(sidesCutedArray[x+1])
                ave = np.average(arrTMP, axis=0)
                result.append(ave)
            result = np.asarray(result)
            result_2 = []
            for x in xrange(0,result.shape[0]-1,2):
                arrTMP = []
                arrTMP.append(result[x])
                arrTMP.append(result[x+1])
                ave = np.average(arrTMP, axis=0)
                result_2.append(ave)
            result_2 = np.asarray(result_2)            
            return result_2.reshape(result_2.shape[0]*result_2.shape[1],)
