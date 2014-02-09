from classifier.classifier import IClassifier
from PyQt4 import QtCore
import numpy as np
import kMeansHelper as kmHelper
import clusterSignal as cSignal
from PyQt4.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt4 import QtGui
import sys, os
import win32com.client
from view.ui_kmeans_visualizer import ViewUIKMeans

class KMeans(IClassifier):
    
    def __init__(self, recorder=None):
        self.name = 'kmeans'
        self.kmeansGUI = False
        self.currentRecordFrame = None
        self.recorder = recorder
        self.kmH = kmHelper.kMeansHepler()
        
        self.kmeans = None
        self.kmeans_16N = None
        self.bufferArray = []
        self.bufferArray_16N = []
        
        self.startGesture = -2
        self.recognizatorBusy = False
        self.currentClass = -3        
        self.startGesture_16N = -2
        self.firstNoneResult_16N = False
        self.currentClass_16N = -3
        self.firstCleanUpMessage = True  
        self.checkOnline = False
        self.startBuffern = False
        
        self.cSignal = cSignal.SignalToGUI()
        self.viewUiKmeans_ = None
        self.percentRatio = 0.0
        self.wasClass4Before = False
        self.wasClass3Before = False
          
        self.classArray = None
        self.recorder.classifyStart(self)
        
        if os.name == 'nt':
            self.isWindows = True
            self.shell = win32com.client.Dispatch("WScript.Shell")
        else:
            self.isWindows = False
        
        
    def startGui(self, recorder, callback):
        self.kmeansGUI = True
        self.app = ViewUIKMeans(self, self.getName, self.cSignal)
        code = self.app.start()
        callback(code)
        
        
    def getName(self):
        return self.name
    

    def startTraining(self, args=[]):
        pass

 
    def classify(self, data):
        
        if self.kmeansGUI:
            cluster_0, cluster_1 = None, None           
            if self.startBuffern:
                self.bufferArray = np.roll(self.bufferArray, -1, axis=0)
                self.bufferArray[47] = self.kmH.normalizeSignalLevelSecond(data)
                if self.checkOnline:
                    result = self.kmH.segmentOneHandGesture(self.bufferArray, outArrayLength=24, leftMargin=4, oneSecPeak=False)
                    if result is not None:
                        result = self.kmH.reduceDimensionality(result, setAxisTo=1, std='cut')
                        result = np.asarray(result)

                        if len(result) == self.kmeans.cluster_centers_.shape[1]:
                            cluster_0 = self.kMeansOnline(result)
                            if cluster_0 == 3:
                                if self.wasClass3Before:
                                    print '------------------------------- by 3'
                                    self.cSignal.emitSignal(10)
                                else:
                                    if self.wasClass4Before:
                                        #sometime came a single 3 after many 4's so this should fix it
                                        self.wasClass4Before = False
                                    else:    
                                        self.wasClass3Before = True
                                        print '        ', cluster_0, '\n'
                                        self.cSignal.emitSignal(10)
                                        self.cSignal.emitSignal(3)
                            elif cluster_0 == 4:
                                if self.wasClass4Before:
                                    print '------------------------------- by 4'
                                    self.cSignal.emitSignal(10)
                                else:
                                    self.wasClass4Before = True
                                    print '            ', cluster_0,'\n'
                                    self.cSignal.emitSignal(4)
                                    self.cSignal.emitSignal(10)
                            else:
                                self.wasClass4Before = False
                                self.wasClass3Before = False
                        else:
                            print 'result length not matched !!!!  : ', len(result)
               
                if self.kmeans_16N is not None:
                    self.bufferArray_16N = np.roll(self.bufferArray_16N, -1, axis=0)
                    self.bufferArray_16N[57] = self.kmH.normalizeSignalLevelSecond(data)
                    if self.checkOnline:
                        result = self.kmH.segmentOneHandGesture(self.bufferArray[0:27,], outArrayLength=24, leftMargin=12, oneSecPeak=True)
                        if result is not None:
                            result = self.kmH.reduceDimensionality(result, setAxisTo=1, std='cut')
                            result = np.asarray(result)
                            if len(result) == self.kmeans_16N.cluster_centers_.shape[1]:
                                cluster_1 = self.kMeansOnline_16N(result)
                                if not self.wasClass4Before and not self.wasClass3Before:
                                    if self.currentClass_16N != cluster_1:
                                        #self.cSignal.emitSignal(cluster_1)
                                        self.currentClass_16N = cluster_1
                                        if cluster_1 == 0:
                                            print  cluster_1, '\n'
                                            if self.isWindows:
                                                self.shell.SendKeys("{PGUP}",0)
                                                self.cSignal.emitSignal(0)
                                                self.cSignal.emitSignal(10)                                            
                                        if cluster_1 == 1:
                                            print '    ', cluster_1, '\n'
                                            if self.isWindows:
                                                self.shell.SendKeys("{PGDN}",0)
                                                self.cSignal.emitSignal(1)
                                                self.cSignal.emitSignal(10)  
                                    else:
                                        if cluster_1 == 0:
                                            print '------------------------------- by 0'
                                            self.cSignal.emitSignal(10)
                                        if cluster_1 == 1:
                                            print '------------------------------- by 1'
                                            self.cSignal.emitSignal(10)
                            else:
                                print 'result length not matched 16N !!!!  : ', len(result)

                if not self.wasClass4Before and not self.wasClass3Before and cluster_1 == 2 and self.firstCleanUpMessage:
                    self.firstCleanUpMessage = False
                    self.cSignal.emitSignal(-10)
                else:
                    self.firstCleanUpMessage = True              
                    
    def setClassArray(self, cArray):
        self.classArray = cArray
    
    
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
        self.bufferArray = np.zeros((48, 64))
        self.bufferArray_16N = np.zeros((58, 64))
        self.startBuffern = True
        print 'fillBuffer'
        print self.bufferArray.shape
        print self.bufferArray_16N.shape
        
    def getBuffer(self):
        return self.bufferArray


    def setKMeans(self, kMeans, kMeans_16N=None):
        self.kmeans = kMeans
        self.kmeans_16N = kMeans_16N     
        
        
    def kMeansOnline(self, checkArray):
        class_  = self.kmeans.transform(checkArray)
        cluster_ =  self.kmH.checkClusterDistance(class_, self.percentRatio)

        if self.classArray is not None:
            clusterArray = np.where(self.classArray==cluster_)[0]
            if clusterArray.size == 1:
                cluster = clusterArray[0] 
                cluster_ = cluster

        return cluster_
    
    
    def kMeansOnline_16N(self, checkArray):
        class_  = self.kmeans_16N.transform(checkArray)
        cluster =  self.kmH.checkClusterDistance(class_, self.percentRatio)
        return cluster   


    def checkKMeansOnline(self):
        self.checkOnline = not self.checkOnline


    def setPercentRatio(self, pRatio):
        self.percentRatio = pRatio    
  
