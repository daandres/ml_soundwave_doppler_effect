from classifier.classifier import IClassifier
from PyQt4 import QtCore
import numpy as np
import kMeansHelper as kmHelper
import clusterSignal as cSignal
from PyQt4.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt4 import QtGui
import sys
from src.view.ui_kmeans_visualizer import ViewUIKMeans

class KMeans(IClassifier):
    
    def __init__(self, recorder=None):
        self.name = 'kmeans'
        
        self.currentRecordFrame = None
        self.recorder = recorder
        self.kmH = kmHelper.kMeansHepler()
        self.kmeans = None
        self.checkOnline = False
        self.startBuffern = False
        
        self.cSignal = cSignal.SignalToGUI()
        self.viewUiKmeans_ = None
        self.percentRatio = 0.0
        self.gestureIdx = 0
        self.gestureArray = []
          
        self.recorder.classifyStart(self)
        
        
        self.startGesture = -2
        self.firstNoneResult = False
        self.currentClass = -3
        
        
    def startGui(self, recorder, callback):
        self.app = ViewUIKMeans(self, self.getName, self.cSignal)
        self.app.start()
        callback()
        
        
    def getName(self):
        return self.name
    

    def startTraining(self, args=[]):
        pass

 
    def classify(self, data):
        '''
        if self.startBuffern:  
            self.bufferArray = np.roll(self.bufferArray, -1, axis=0)
            self.bufferArray[self.bufferSize-1] = self.kmH.normalizeSignalLevelSecond(data)
            
            if self.checkOnline:
                result = self.kmH.reduceDimensionality(self.bufferArray)
                if result is not None:
                        result = np.asarray(result)
                        result = result.reshape(result.shape[0]*result.shape[1])
                if len(result) == self.kmeans.cluster_centers_.shape[1]:
                    self.kMeansOnline(result)
                else:
                    print 'result length not matched !!!!  : ', len(result)
                    
        '''            
        if self.startBuffern:
            
            self.bufferArray = np.roll(self.bufferArray, -1, axis=0)
            # war gut bei 47
            self.bufferArray[25] = self.kmH.normalizeSignalLevelSecond(data)
            if self.checkOnline:
                # es hal bei 16 staat 24 funktionietrt ?!?!?!?!
                result = self.kmH.segmentOneHandGesture(self.bufferArray, outArrayLength=16, leftMargin=8, oneSecPeak=True)
                #print np.asarray(result).shape
                if result is not None:
                    self.firstNoneResult = True
                    result = self.kmH.reduceDimensionality(result)
                    result = np.asarray(result)
                    #xxx
                    #result = result.reshape(result.shape[0]*result.shape[1])
                    
                    if len(result) == self.kmeans.cluster_centers_.shape[1]:
                        cluster_ = self.kMeansOnline(result)
                        if self.currentClass != cluster_:
                            self.cSignal.emitSignal(cluster_)
                            self.currentClass = cluster_
                            print result.shape
                        else:
                            self.cSignal.emitSignal(-2)
                    else:
                        print 'result length not matched !!!!  : ', len(result)
                else:
                    if self.firstNoneResult:
                        self.cSignal.emitSignal(-2)
                        self.firstNoneResult = False
                    
                    
    def startValidation(self):
        pass

 
    def load(self, filename=""):
        pass

 
    def save(self, filename=""):
        print 'jojo'
        pass

 
    def loadData(self, filename=""):
        pass

 
    def saveData(self, filename=""):
        pass

 
    def printClassifier(self):
        pass


    def fillBuffer(self, bufferSize):
        self.bufferSize = bufferSize
        #self.bufferArray = np.zeros((self.bufferSize, 64))
        #war gut bei 48
        self.bufferArray = np.zeros((26, 64))
        self.startBuffern = True
        print 'fillBuffer'
        print self.bufferArray.shape
        
    def getBuffer(self):
        return self.bufferArray


    def setKMeans(self, kMeans):
        self.kmeans = kMeans
        self.gestureArray = np.array(['bob\n', 'bob\n', 'bob\n', 'bob\n', 'bob\n', 'bob\n', 'bob\n', 'bob\n', 'bob\n', 'bob\n'])
        
        
        
    def kMeansOnline(self, checkArray):
        class_  = self.kmeans.transform(checkArray)
        cluster =  self.kmH.checkClusterDistance(class_, self.percentRatio)
        self.setGestureArray(cluster)
        
        #self.cSignal.emitSignal(cluster)
        
        if cluster == -1:
            print '-1'
        elif cluster == 0:
            print '    0'
        elif cluster == 1:
            print '        1'
        elif cluster == 2:
            print '            2'
        elif cluster == 3:
            print '                3'
        elif cluster == 4:
            print '                    4'
        elif cluster == 5:
            print '                        5'
        elif cluster == 6:
            print '                            6'
        elif cluster == 7:
            print '                                7'                                                
        
        return cluster
    
    
    def setGestureArray(self, cluster):
        self.gestureIdx = self.gestureIdx+1 
        class_ = "-"
        if cluster == -1:
            class_ = '\t-1\n'
        elif cluster == 0:
            class_ = '\t\t0\n'
        elif cluster == 1:
            class_ = '\t\t\t1\n'
        elif cluster == 2:
            class_ = '\t\t\t\t2\n'
        elif cluster == 3:
            class_ = '\t\t\t\t\t3\n'
        elif cluster == 4:
            class_ = '\t\t\t\t\t\t4\n'
        elif cluster == 5:
            class_ = '\t\t\t\t\t\t\t5\n'
        elif cluster == 6:
            class_ = '\t\t\t\t\t\t\t\t6\n'
        elif cluster == 7:
            class_ = '\t\t\t\t\t\t\t\t7\n'
   
        
        self.gestureArray[self.gestureIdx] = class_
        self.gestureIdx = (self.gestureIdx+1)%9                                           
    
    
    def getGestureArray(self):
        return np.asarray(self.gestureArray)
    
        
    def checkKMeansOnline(self):
        self.checkOnline = not self.checkOnline
    #new
    def setPercentRatio(self, pRatio):
        self.percentRatio = pRatio    
    #bob end
