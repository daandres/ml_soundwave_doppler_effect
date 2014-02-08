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
        self.firstNoneResult = False
        self.currentClass = -3        
        self.startGesture_16N = -2
        self.firstNoneResult_16N = False
        self.currentClass_16N = -3
        
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
        #self.cSignal.emitFrame(np.array())
        if self.kmeansGUI:
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
                self.bufferArray[47] = self.kmH.normalizeSignalLevelSecond(data)
                if self.checkOnline:
                    # es hal bei 16 staat 24 funktionietrt ?!?!?!?! self.bufferArray[0:24,::]
                    result = self.kmH.segmentOneHandGesture(self.bufferArray, outArrayLength=24, leftMargin=4, oneSecPeak=False)
                    #result = self.kmH.segmentOneHandGesture(self.bufferArray, outArrayLength=24, leftMargin=12, oneSecPeak=True)
                    #print np.asarray(result).shape
                    if result is not None:
                        self.firstNoneResult = True
                        result = self.kmH.reduceDimensionality(result, setAxisTo=1, std='cut')
                        result = np.asarray(result)
                        #xxx
                        #result = result.reshape(result.shape[0]*result.shape[1])
                        
                        if len(result) == self.kmeans.cluster_centers_.shape[1]:
                            cluster_ = self.kMeansOnline(result)
                            if cluster_ == 3:
                                if self.wasClass3Before:
                                    print '------------------------------- by 3'
                                else:
                                    self.wasClass3Before = True
                                    print '        ', cluster_, '\n'
                                    self.cSignal.emitSignal(3)
                            elif cluster_ == 4:
                                if self.wasClass4Before:
                                    print '------------------------------- by 4'
                                else:
                                    self.wasClass4Before = True
                                    print '            ', cluster_,'\n'
                                    self.cSignal.emitSignal(4)
                            else:
                                self.wasClass4Before = False
                                self.wasClass3Before = False
                            '''
                            if self.currentClass != cluster_:
                                #print 'cluster_ ', cluster_
                                if cluster_ == 3: 
                                    print 'cluster_ ', cluster_
                                    self.blockSecond = True
                                elif cluster_ == 4:
                                    print 'cluster_ ', cluster_
                                    self.blockSecond = True
                                    #self.cSignal.emitSignal(cluster_)
                                    self.currentClass = cluster_
                                #print result.shape
                            else:
                                pass
                                #self.cSignal.emitSignal(-2)
                            '''
                        else:
                            print 'result length not matched !!!!  : ', len(result)
                    else:
                        if self.firstNoneResult:
                            #self.cSignal.emitSignal(-2)
                            self.firstNoneResult = False
               
                if self.kmeans_16N is not None:
                    self.bufferArray_16N = np.roll(self.bufferArray_16N, -1, axis=0)
                    # war gut bei 47
                    self.bufferArray_16N[57] = self.kmH.normalizeSignalLevelSecond(data)
                    if self.checkOnline:
                        # es hal bei 16 staat 24 funktionietrt ?!?!?!?!
                        result = self.kmH.segmentOneHandGesture(self.bufferArray[0:27,], outArrayLength=24, leftMargin=12, oneSecPeak=True)
                        #print np.asarray(result).shape
                        if result is not None:
                            self.firstNoneResult_16N = True
                            result = self.kmH.reduceDimensionality(result, setAxisTo=1, std='cut')
                            result = np.asarray(result)
                            #xxx
                            #result = result.reshape(result.shape[0]*result.shape[1])
                            
                            if len(result) == self.kmeans_16N.cluster_centers_.shape[1]:
                                cluster_ = self.kMeansOnline_16N(result)
                                #print cluster_, 'ohne vorselect' 
                                
                                if not self.wasClass4Before and not self.wasClass3Before:
                                    if self.currentClass_16N != cluster_:
                                        #self.cSignal.emitSignal(cluster_)
                                        self.currentClass_16N = cluster_
                                        if cluster_ == 0:
                                            print  cluster_, '\n'
                                            if self.isWindows:
                                                self.shell.SendKeys("{PGUP}",0)                                            
                                        if cluster_ == 1:
                                            print '    ', cluster_, '\n'
                                            if self.isWindows:
                                                self.shell.SendKeys("{PGDN}",0)  

                                    else:
                                        print '-------------------------------', cluster_
                                        #self.cSignal.emitSignal(-2)
                            else:
                                print 'result length not matched 16N !!!!  : ', len(result)
                        else:
                            if self.firstNoneResult_16N:
                                #self.cSignal.emitSignal(-2)
                                self.firstNoneResult_16N = False                    
                
                
                ''' 
                if self.kmeans_16N is not None:
                    self.bufferArray_16N = np.roll(self.bufferArray_16N, -1, axis=0)
                    # war gut bei 47
                    self.bufferArray_16N[25] = self.kmH.normalizeSignalLevelSecond(data)
                    if self.checkOnline:
                        # es hal bei 16 staat 24 funktionietrt ?!?!?!?!
                        result = self.kmH.segmentOneHandGesture(self.bufferArray_16N, outArrayLength=16, leftMargin=8, oneSecPeak=True)
                        #print np.asarray(result).shape
                        if result is not None:
                            self.firstNoneResult_16N = True
                            result = self.kmH.reduceDimensionality(result, sidesCut=20, setAxisTo=0)
                            result = np.asarray(result)
                            #xxx
                            #result = result.reshape(result.shape[0]*result.shape[1])
                            
                            if len(result) == self.kmeans_16N.cluster_centers_.shape[1]:
                                cluster_ = self.kMeansOnline_16N(result)
                                if self.currentClass_16N != cluster_:
                                    self.cSignal.emitSignal(cluster_)
                                    self.currentClass_16N = cluster_
                                    #print result.shape
                                else:
                                    self.cSignal.emitSignal(-2)
                            else:
                                print 'result length not matched 16N !!!!  : ', len(result)
                        else:
                            if self.firstNoneResult_16N:
                                self.cSignal.emitSignal(-2)
                                self.firstNoneResult_16N = False      
                '''  
   
                                
                                   
                    
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
        #self.bufferArray = np.zeros((self.bufferSize, 64))
        #war gut bei 48
        self.bufferArray = np.zeros((48, 64))
        self.bufferArray_16N = np.zeros((58, 64))
        #self.bufferArray_16N = np.zeros((26, 64))
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
                '''
                if cluster == -1:
                    print '-1'
                elif cluster == 0:
                    pass#print '    0'
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
                '''
        return cluster_
    
    
    def kMeansOnline_16N(self, checkArray):
        class_  = self.kmeans_16N.transform(checkArray)
        cluster =  self.kmH.checkClusterDistance(class_, self.percentRatio)
        '''
        if cluster == -1:
            print '-1'
        elif cluster == 0:
            print '    c0'
        elif cluster == 1:
            print '        c1'
        elif cluster == 2:
            print '            c2'
        elif cluster == 3:
            print '                c3'
        elif cluster == 4:
            print '                    c4'
        elif cluster == 5:
            print '                        c5'
        elif cluster == 6:
            print '                            c6'
        elif cluster == 7:
            print '                                c7'                                                
        '''
        return cluster   

    def checkKMeansOnline(self):
        self.checkOnline = not self.checkOnline
    #new
    def setPercentRatio(self, pRatio):
        self.percentRatio = pRatio    
    #bob end
