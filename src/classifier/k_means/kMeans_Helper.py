
import numpy as np

import sys, os
from PyQt4 import Qt, QtCore, QtGui
from PyQt4.QtGui import QMainWindow, QPushButton, QApplication
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *
from threading import Thread
from properties.config import ConfigProvider
import time
import ntpath

from functools import partial




from sklearn import cluster, svm 

import copy
import numpy as np
from scipy import stats


class kMeansHepler():
    '''
    def segmentInputData(self, inArray, outArrayLength, levelTH=0.15, wideTH ):
        
        result = []
        for idx, frame in enumerate(inArray):
            
            maxV = np.amax(frame)
            maxP = np.argmax(frame)
            # Where values are higher than levelTH% of max
            idxH = frame > maxV * levelTH
            print 'idx : ', idx, '    wide :     ',  np.sum(idxH)#, 'mode : ', stats.mode(frame)
            result.append(np.sum(idxH))
        
        
        
        #return stats.mode(result)
        '''
        
    ''' check one gesture after segmentation '''
    ''' because of k=2 we can hopefully see how good or bed were the thresholds set for segmentation '''
    ''' return the amount of similar class '''   
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
        

    def segmentOneHandGesture(self, inArray, outArrayLength=16, leftMargin=3, oneSecPeak=True):
        
        globalRatio = 0.0
        matchFrameIdx = 0
        resultArray = None
        globalMax = np.amax(inArray)
        firstRightPeak = True
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

    def reshapeArray2DTo3D64(self, inArray2D):
        frames = inArray2D.shape[1]/64
        return inArray2D.reshape(inArray2D.shape[0], frames, 64) 
         
         
    def reshapeArray3DTo2D64(self, inArray3D):
        return inArray3D.reshape(inArray3D.shape[0], inArray3D.shape[1]*inArray3D.shape[2],) 
    
    def checkClusterDistance(self, disToCentre, perRatio=10):
        #sortedDistance = disToCentre[0].argsort()[-2:][::-1]
        #distanceRatio = disToCentre[0][sortedDistance[0]]/disToCentre[0][sortedDistance[1]]
        sortedDistance = np.argsort(disToCentre[0])
        distanceRatio = disToCentre[0][sortedDistance[1]]/disToCentre[0][sortedDistance[0]]  
        if distanceRatio > 1. + perRatio/100.:
            return sortedDistance[0]
        else:
            return -1   
    
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

    
    def segmentInputData(self, inArray, outArrayLength=16, levelTH=0.1, wideTH=1, normalize=True, newMaxV=800, gradations=10  ):
        
        wideList = []
        for frame in inArray:
            frame_ = frame
            if normalize:
                frame_ = self.normalizeSignalLevel(frame, newMaxV, gradations)
            # Where values are higher than levelTH% of max
            maxV = np.amax(frame_)
            idxH = frame_ > maxV * levelTH
            wideList.append(np.sum(idxH))
        
        mode, count = stats.mode(wideList)
        
        # don't care or adjust levelTH
        if mode.shape[0] > 1:
            print 'mode ', int(mode)
            return None
        #print 'mode ', int(mode)
        #print 'count ', count[0]
        # levetTH to height adjust or don't care
        #if count[0] < inArray.shape[1]/4:
            #print 'count ', count[0], ', inArray.shape ', float(inArray.shape[0])/4.0
            #return None
        
        idxOut = 0
        resultNorm = []
        result = []
        appendToOutpuArr = False

        for idx,  frame in enumerate(inArray):
            frame_ = frame
            if normalize:
                frame_ = self.normalizeSignalLevel(frame, newMaxV, gradations)
            maxV = np.amax(frame_)
            if (np.sum(frame_ > maxV * levelTH)) - wideTH > int(mode):
                #print 'idx ', idx
                appendToOutpuArr = True
            if appendToOutpuArr and idxOut < outArrayLength:
                idxOut +=1
                resultNorm.append(frame_)
                result.append(frame)
        
        endResultNorm = np.asarray(resultNorm)
        endResult = np.asarray(result)
        
        if endResultNorm.shape[0] is not outArrayLength:
            endResultNorm = None
            endResult = None
        return endResultNorm, endResult


    def normalizeSignalLevel(self, frame, newMaxV, gradations):
        maxV = np.amax(frame)
        maxP = np.argmax(frame)
        
        result = copy.copy(frame)
        result[maxP] = newMaxV   
        
        for x in xrange(len(frame)):
            result[x] = (float(int((frame[x] / frame[maxP])*gradations)))/gradations*newMaxV
        result[maxP] = newMaxV
        
        return result

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
    
    def normalize3DArray(self, inArray3D):
        result = []
        for gesture in inArray3D:
            gestureTMP = []
            for frame in gesture:
                gestureTMP.append(self.normalizeSignalLevelSecond(frame))
            result.append(gestureTMP)
            
        return np.asarray(result)
    
    def reduceDimensionality(self, inArray, sidesCut=16, manyTimes=4):
        
        result = []
        for x in xrange(0,inArray.shape[0]-1,2):
            arrTMP = []
            arrTMP.append(inArray[x][sidesCut:(inArray.shape[1]-sidesCut)])
            arrTMP.append(inArray[x+1][sidesCut:(inArray.shape[1]-sidesCut)])
            #print 'arrTMP.shape ', np.asarray(arrTMP).shape
            ave = np.average(arrTMP, axis=0)
            #print 'ave.shape ', np.asarray(ave).shape
            '''
            if manyTimes > 1:
                ave2 = np.asarray(ave)
                ave = ave2.reshape(2,ave2.shape[0]/2) 
                #print 'ave2.reshape', np.asarray(ave.shape)  
                ave = np.average(ave, axis=0)
                #print 'ave2.shape', np.asarray(ave.shape)
            '''    
            result.append(ave)
        '''
        if manyTimes > 2:
            ave3 = np.asarray(result)
            #print 'ave3.shape ', ave3 
            ave3 = ave3.reshape(ave3.shape[0]/2,2,ave3.shape[1])
            #print 'ave3.shape', np.asarray(ave3.shape)
            result = np.average(ave3, axis=1)
        
        if manyTimes > 3:
            ave4 = np.asarray(result)
            #print 'ave3.shape ', ave3 
            ave4 = ave4.reshape(ave4.shape[0]/2,2,ave4.shape[1])
            #print 'ave3.shape', np.asarray(ave3.shape)
            result = np.average(ave4, axis=1)
        if True:#manyTimes > 3:
            ave5 = np.asarray(result)
            #print 'ave3.shape ', ave3 
            ave5 = ave5.reshape(ave5.shape[0]/2,2,ave5.shape[1])
            #print 'ave3.shape', np.asarray(ave3.shape)
            result = np.average(ave5, axis=1)
        '''                
        return np.asarray(result)
                         
   
   