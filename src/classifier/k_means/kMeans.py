from classifier.classifier import IClassifier
from PyQt4 import QtCore
import numpy as np
import kMeansHelper as kmHelper
import clusterSignal as cSignal
from PyQt4.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt4 import QtGui
import sys
from src.view.ui_kmeans_visualizer import ViewUIKMeans
id = QtCore.QMetaType.type('ViewUIKMeans')
class KMeans(IClassifier):
    
    def __init__(self, recorder=None):
        self.name = 'kmeans'
        self.currentRecordFrame = None
        
        self.recorder = recorder
        #bob
        self.kmH = kmHelper.kMeansHepler()
        self.kmeans = None
        self.checkOnline = False
        self.startBuffern = False
        
        self.cSignal = cSignal.SignalToGUI()
        #self.cSignal.currentGestureSignal.connect(self.setGestureTrigger)
        self.viewUiKmeans_ = None
        self.percentRatio = 0.0
        self.gestureIdx = 0
        self.gestureArray = []
          
        self.recorder.classifyStart(self)
        
        
    def startGui(self, recorder, callback):
        self.app = ViewUIKMeans(self, self.getName)
        self.app.start()
        callback()
        
        
    def getName(self):
        return self.name
    

    def startTraining(self, args=[]):
        
        

        pass
        #self.recorder.classifyStart(self)

        #self.viewUiKmeans_ = ViewUIKMeans(self, self.getName)
        #self.viewUiKmeans_.startNewThread()
        #self.cSignal = self.viewUiKmeans_.macheCrash#cSignal#.SignalToGUI(parent=self.viewUiKmeans_)       

 
    def classify(self, data):
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


    
    @pyqtSlot(int)
    def setGestureTrigger(self, gesture):
        print 'gesture : ', gesture
            
    
    def jojo(self):
        return 
    
    def startValidation(self):
        pass

 
    def load(self, filename=""):
        pass

 
    def save(self, filename=""):
        pass

 
    def loadData(self, filename=""):
        pass

 
    def saveData(self, filename=""):
        pass

 
    def printClassifier(self):
        pass


    def fillBuffer(self, bufferSize):
        self.bufferSize = bufferSize
        self.bufferArray = np.zeros((self.bufferSize, 64))
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
        
        self.cSignal.emitSignal(cluster)
        
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
