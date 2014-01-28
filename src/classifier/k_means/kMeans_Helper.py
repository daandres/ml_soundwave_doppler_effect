import view.ui_bob
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
from classifier.k_means.kMeans import kmeans



from sklearn import cluster, svm 

import copy
import numpy as np
from scipy import stats
'''
from enum import Enum
class CallbackMessage():
    bufferFilled = 1
    progress = 2 
    checkKMeans = 3
'''    
    

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
        
    def segmentInputData(self, inArray, outArrayLength, levelTH, wideTH, normalize=False, newMaxV=800, gradations=10  ):
        
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
        result = []
        appendToOutpuArr = False
        if count[0] > float(inArray.shape[0])/4.0:
            appendToOutpuArr = True    
        for idx,  frame in enumerate(inArray):
            frame_ = frame
            if normalize:
                frame_ = frame#self.normalizeSignalLevel(frame, newMaxV, gradations)
            maxV = np.amax(frame_)
            if (np.sum(frame_ > maxV * levelTH)) - 1 > int(mode):
                appendToOutpuArr = True
            if appendToOutpuArr and idxOut < outArrayLength:
                idxOut +=1
                result.append(frame_)
        
        endResult = np.asarray(result)
        if endResult.shape[0] is not outArrayLength:
            endResult = None
        
        return endResult


    def normalizeSignalLevel(self, frame, newMaxV, gradations):
        maxV = np.amax(frame)
        maxP = np.argmax(frame)
        
        result = copy.copy(frame)
        result[maxP] = newMaxV   
        
        for x in xrange(len(frame)):
            result[x] = (float(int((frame[x] / frame[maxP])*gradations)))/gradations*newMaxV
        result[maxP] = newMaxV
        
        return result

    def reduceDimensionality(self, inArray, sidesCut=16, manyTimes=4):
        
        result = []
        for x in xrange(0,inArray.shape[0]-1,2):
            arrTMP = []
            arrTMP.append(inArray[x][sidesCut:(inArray.shape[1]-sidesCut)])
            arrTMP.append(inArray[x+1][sidesCut:(inArray.shape[1]-sidesCut)])
            #print 'arrTMP.shape ', np.asarray(arrTMP).shape
            ave = np.average(arrTMP, axis=0)
            #print 'ave.shape ', np.asarray(ave).shape
            
            if manyTimes > 1:
                ave2 = np.asarray(ave)
                ave = ave2.reshape(2,ave2.shape[0]/2) 
                #print 'ave2.reshape', np.asarray(ave.shape)  
                ave = np.average(ave, axis=0)
                #print 'ave2.shape', np.asarray(ave.shape)
            result.append(ave)
        
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
            
        return np.asarray(result)
                         
   
   