import ui_kmeans as ui_kmeans_
import numpy as np

import sys, os
from PyQt4 import Qt, QtCore, QtGui
from PyQt4.QtGui import QMainWindow, QPushButton, QApplication
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *
from threading import Thread

import copy
import ntpath
from functools import partial

from sklearn import cluster
import classifier.k_means.kMeansHelper as kmHelper
from properties.config import ConfigProvider
from PyQt4.Qt import QColor


class ViewUIKMeans:
    def __init__(self, kMeansClassifier=None, applicationClose=None):

        self.kmH = None 
        self.kmeans = None
        self.kmeansClusterCenters = None
        
        self.checkOnline = False
        
        self.toogleClass0 = False
        self.toogleClass1 = False
        self.toogleClass2 = False
        self.toogleClass3 = False
        self.toogleClass4 = False
        self.toogleClass5 = False
        self.toogleClass6 = False
        self.toogleClass7 = False
        
        self.idxLeft = 20
        self.idxRight = 44

        self.plot_id = 1
        self.framesToSkip = 1
        self.arraySidesCut = 0
       
        self.showRecords = False
        self.recordFramesCount = 32
    
        self.noiseArray = []
        self.arrayFromFile = []
        self.globalViewArray = []
        self.learnArrayKMeans = []
        self.arrayFromFileViewShape = []
        self.arrayFromFileViewShapeNorm = []
        self.preselectedByKMeansArray = []
        
        self.textEdit = None
        self.globalLabelText = 'Init!\n'
        self.segNormArray = []
        
        self.c0, self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7 = False, False, False, False, False, False, False, False
        self.showClusterList = [ self.c0, self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7 ]
        
        # xDummies
        self.xPoints = np.arange(64)
        
        self.fileName = None
        self.multipleFiles = False
        self.openFileDirectory = "C:/Users/Robert/git/ml_soundwave_doppler_effect/gestures/Robert"
        self.centroidsFileDirectory = "C:/Users/Robert/git/ml_soundwave_doppler_effect/gestures/Robert/Centroids"
        self.app = None
        if kMeansClassifier == None:
            raise Exception("No kMeansClassifier, so go home")
        self.kMeansClassifier = kMeansClassifier
        self.recorder = kMeansClassifier.recorder
        
        if applicationClose == None:
            raise Exception("No close callback")
        self.applicationClose = applicationClose
       
        self.uiplot_tab1, self.curve_tab1, self.curve_2_tab1 = None, None, None
       
        self.curve_1, self.curve_2, self.curve_3, self.curve_4, self.curve_5, self.curve_6, self.curve_7, self.curve_8 = Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()
        self.curve_9, self.curve_10, self.curve_11, self.curve_12, self.curve_13, self.curve_14, self.curve_15, self.curve_16 = Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()
        self.curve_17, self.curve_18, self.curve_19, self.curve_20, self.curve_21, self.curve_22, self.curve_23, self.curve_24 = Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()
        self.curve_25, self.curve_26, self.curve_27, self.curve_28, self.curve_29, self.curve_30, self.curve_31, self.curve_32 = Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()
        
        self.curveList = [  self.curve_1 , self.curve_2 , self.curve_3 , self.curve_4 , self.curve_5 , self.curve_6 , self.curve_7 ,self.curve_8,
                            self.curve_9 ,self.curve_10 ,self.curve_11 ,self.curve_12 ,self.curve_13 ,self.curve_14 , self.curve_15 , self.curve_16,
                            self.curve_17 , self.curve_18 , self.curve_19 , self.curve_20 , self.curve_21 , self.curve_22 , self.curve_23 , self.curve_24,
                            self.curve_25 , self.curve_26 ,self.curve_27 ,self.curve_28 ,self.curve_29 ,self.curve_30 ,self.curve_31 ,self.curve_32]
        
        config = ConfigProvider()
        self.amplitude = float(config.getAudioConfig()['amplitude'])
        self.guiIntervall = float(config.getRecordConfig()['guiintervall'])
        self.sampleRate = int(float(config.getRecordConfig()['leftborder']) + float(config.getRecordConfig()['rightborder']))

     
    def plotSignal(self):

        data = self.recorder.getTransformedData()
        if data == None:
            return
        xs, ys = data
        
        ys = ys[self.idxLeft:self.idxRight]
        xs = self.xPoints[self.idxLeft:self.idxRight]
        
        if not self.showRecords:
       
            i = self.plot_id
            qwtPlot = getattr(self.uiplot ,'qwtPlot_%d' %i)
            curr = getattr(self ,'curve_%d' %i)
            self.plot_id = self.plot_id +1
            
            curr.setData(xs, ys)
            qwtPlot.replot()
            
            if self.plot_id == 33:
                self.plot_id = 1
        
        if self.checkOnline:
            #self.toogleForClass()
              
            #text = self.recorder.getGestureArray()
            #self.textEdit.setText(text.tostring())
            #self.textEdit.moveCursor(QtGui.QTextCursor.End)
            text = np.array(['\ta\n','b\n','\tc\n'])
            self.textEdit.setText(text.tostring())
            
   
    def toogleForClass(self):
        for x in xrange(8):
            classBool = self.recorder.toogleClassList[x]
            classButton = getattr(self.uiplot,'class%d_bt' %x)  
            if classBool:
                classButton.setStyleSheet(self.getButtonColor(x))
            else:
                classButton.setStyleSheet('QPushButton {color: black; background-color: grey; font: bold;}')
 
            
    def getButtonColor(self, classNumber, button=True):
        startString = 'QPushButton {color: black; background-color:'
        endString = '; font: bold;}'
        result = None
        if classNumber == 0:
            result = startString + 'blue' + endString if button else Qt.Qt.blue
        elif classNumber == 1:
            result = startString + 'green' + endString if button else Qt.Qt.darkGreen  
        elif classNumber == 2:
            result = startString + 'red' + endString if button else Qt.Qt.red
        elif classNumber == 3:
            result = startString + 'white' + endString if button else Qt.Qt.black
        elif classNumber == 4:
            result = startString + 'darkGray' + endString if button else Qt.Qt.darkGray   
        elif classNumber == 5:
            result = startString + 'darkMagenta' + endString if button else Qt.Qt.darkMagenta   
        elif classNumber == 6:
            result = startString + 'darkYellow' + endString if button else Qt.Qt.darkYellow  
        elif classNumber == 7:
            result = startString + 'darkCyan' + endString if button else Qt.Qt.darkCyan  
        return result
 
 
    def recordByRecorder(self):
        self.recordFramesCount = self.uiplot.frames_sb.value()
        self.kMeansClassifier.fillBuffer(self.recordFramesCount, self.callback)
        #self.recorder.fillBuffer(self.recordFramesCount, self.callback)
        self.uiplot.record_bt.setStyleSheet('QPushButton {color: green}')
        

    def showPlot(self):
        self.showRecords = False
      
        
        
    def openFile(self):
        print QtCore.QDir.currentPath()
        self.fileName = QtGui.QFileDialog.getOpenFileNames(self.win_plot, "Open ",
                self.openFileDirectory, "*.kmeans")
        if len(self.fileName) == 0:
            self.addLogText('no file was chosen !')
            return
        
        ppath = str(self.fixpath(self.fileName[0]))
        print ppath
        path = ntpath.dirname(ppath)
        print path
        self.openFileDirectory = path
        paths = self.fileName
       
        if not self.multipleFiles:
            classButton = getattr(self.uiplot,'class%s_bt' %path[-1::])
            classButton.setStyleSheet('QPushButton {color: black; background-color: blue; font: bold;}')        
            for idx, path in enumerate(paths):
                if idx == 0:
                    self.arrayFromFile = np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))
                    print 'load array shape : ', self.arrayFromFile.shape
                else:
                    self.arrayFromFile = np.concatenate((self.arrayFromFile, np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))), axis=0)
                    print 'load array shape : ', self.arrayFromFile.shape
        else:
            for path in paths:
                if self.arrayFromFile == None:
                    self.arrayFromFile = np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))
                    print 'load array shape : ', self.arrayFromFile.shape
                else:
                    self.arrayFromFile = np.concatenate((self.arrayFromFile, np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))), axis=0)
                    print 'load array shape : ', self.arrayFromFile.shape
        #self.getArrayFromFile()
        
        
    def fixpath(self, path):
        return path.replace('\\', '/')
    

    def loadMeanArrays(self):
        arr = copy.copy(self.arrayFromFile)
        print arr.shape

        self.learnArrayKMeans = arr
        
        noisArrayTMP = []
        if len(self.noiseArray) == 0:
            print 'noise array empty'
        else:
            # add noise to lern array
            reshapedNoiseArray = self.noiseArray.reshape(self.noiseArray.shape[0],16,64)
           
            for x in xrange(reshapedNoiseArray.shape[0]):

                result = self.kmH.reduceDimensionality(reshapedNoiseArray[x])
                if result is not None:
                    #print result.shape
                    result = np.asarray(result)
                    result = result.reshape(result.shape[0]*result.shape[1])
                   
                    noisArrayTMP.append(result)
                    #print result
                else:
                    print 'array empty !!!'
        noisArrayTMP = np.asarray(noisArrayTMP)
        print 'noisArrayTMP.shape : ', noisArrayTMP.shape           
        self.learnArrayKMeans = np.concatenate((self.learnArrayKMeans, noisArrayTMP))
        print 'self.learnArrayKMeans.shape after add noise : ', self.learnArrayKMeans.shape 
                      

    def loadArrayFromFile(self):
        arr = copy.copy(self.arrayFromFile)
        self.addLogText('load files with shape')
        self.addLogText(arr.shape)
        if len(arr.shape) == 1:
            self.learnArrayKMeans = arr.reshape((1,arr.shape))
            frames = arr.shape/64
            arr = arr.reshape((1, frames, 64))
            self.learnArray = np.asarray(arr)
            self.learnArrayKMeans = arr.reshape((1,arr.shape))
        else:
            frames = arr.shape[1]/64
            arr = arr.reshape(arr.shape[0],frames,64)
            self.arrayFromFileViewShape = arr
        
        self.addLogText('view array shape')
        self.arrayFromFileViewShape = np.asarray(self.arrayFromFileViewShape)
        self.addLogText(self.arrayFromFileViewShape.shape)
        self.arrayFromFileViewShapeNorm = self.kmH.normalize3DArray(self.arrayFromFileViewShape)        
        self.setGlobalViewArray(1)
   
    
    
    def setViewCase(self, case, value ):
        yOrN = False if value == 0 else True
        if yOrN:
            self.setGlobalViewArray(case)
        
   
    def setGlobalViewArray(self, case):
        if case == 1:
            self.globalViewArray = self.arrayFromFileViewShape
        elif case == 2:
            self.globalViewArray = self.arrayFromFileViewShapeNorm
        elif case == 3:
            self.globalViewArray = self.segNormArray
        elif case == 4:
            self.globalViewArray = self.preselectedByKMeansArray
            
        self.globalViewArray = np.asarray(self.globalViewArray)
        
        
    def showGlobalViewArray(self):
        self.showRecords = True
        rAIdx = self.uiplot.arrayIdxLF_sb.value()
        skipFrames = self.uiplot.skipFramesLA_sb.value()
        
        if len(self.globalViewArray) == 0:
            return
        
        if rAIdx < self.globalViewArray.shape[0]:
            viewArray = self.globalViewArray[rAIdx]
        else:
            self.uiplot.arrayIdxLF_sb.setValue(self.globalViewArray.shape[0])
            viewArray = self.globalViewArray[self.globalViewArray.shape[0]-1]
            
        for i in range (0,32):
            idx = i+1
            qwtPlot = getattr(self.uiplot ,'qwtPlot_%d' %idx)
            curr = getattr(self ,'curve_%d' %idx)
            
            if i + skipFrames < len(viewArray):
                ys = viewArray[i+skipFrames]
                ys = ys[self.idxLeft:self.idxRight]
            else:
                ys = np.arange(0,640,10)
                ys = ys[self.idxLeft:self.idxRight]
            xs = self.xPoints[self.idxLeft:self.idxRight]
                       
            curr.setData(xs, ys)
            qwtPlot.replot()
     

    def presortBy2Cluster(self, inArray):
        percent, cluster_, mode, kM = self.kmH.checkKMeansForSegmentation(inArray)
        b = cluster_ == mode
        return inArray[b]


    def segmentClasses(self, classNumber ):
        classButton = getattr(self.uiplot,'class%d_bt' %classNumber)
        classButton.setStyleSheet('QPushButton {color: black; background-color: grey; font: bold;}')  
        arr = copy.copy(self.arrayFromFile) #shape (x, recordingFrames * 64) 
        frames = arr.shape[1]/64
        arr = arr.reshape(arr.shape[0],frames,64) #shape (x, recordingFrames, 64)
        #decide if is better
        arr = self.kmH.normalize3DArray(arr)
        endSegArray = []
        margin = self.uiplot.segMargin_sb.value()
        for gesture in arr:
            segGesture = None
            if classNumber == 0:
                #right-To-Left-One-Hand
                #segGesture = self.kmH.segmentOneHandGesture(gesture, leftMargin=4, oneSecPeak=False)
                segGesture = self.kmH.segmentOneHandGesture(gesture, leftMargin=margin, oneSecPeak=False)
            elif classNumber == 1:
                #top-to-Bottom-One-Hand
                #segGesture = self.kmH.segmentOneHandGesture(gesture, leftMargin=4, oneSecPeak=True)
                segGesture = self.kmH.segmentOneHandGesture(gesture, leftMargin=margin, oneSecPeak=True)
            elif classNumber == 2:
                #opposed with two hands
                #segGesture = self.kmH.segmnetTwoHandsGesture(gesture, leftMargin=3)7
                segGesture = self.kmH.segmnetTwoHandsGesture(gesture, leftMargin=3)                            
            elif classNumber == 3:
                #single-push with one hand
                #segGesture = self.kmH.segmentOneHandGesture(gesture, leftMargin=4, oneSecPeak=False)
                segGesture = self.kmH.segmentOneHandGesture(gesture, leftMargin=margin, oneSecPeak=False)
            elif classNumber == 4:
                #double-push with one hand #long period gesture so small left margin 
                #segGesture = self.kmH.segmentOneHandGesture(gesture, leftMargin=1, oneSecPeak=False)                
                segGesture = self.kmH.segmentOneHandGesture(gesture, leftMargin=margin, oneSecPeak=False)
            if segGesture is not None:
                endSegArray.append(segGesture)
            else:
                print 'segGesture == None'
        
        self.addLogText('segment class finished ! ')
        endSegArray = np.asarray(endSegArray)
        self.segNormArray = endSegArray
        self.addLogText('shape before preselect ', endSegArray.shape)        

        #check if a sort by two clusters help get better results
        self.preselectedByKMeansArray = self.presortBy2Cluster(self.kmH.reshapeArray3DTo2D64(endSegArray))
        self.preselectedByKMeansArray = np.asarray(self.preselectedByKMeansArray)
        self.preselectedByKMeansArray = self.kmH.reshapeArray2DTo3D64(self.preselectedByKMeansArray)
        self.addLogText('shape after preselect ', self.preselectedByKMeansArray.shape)


    def initKMeans(self):     
        maxIterations = self.uiplot.maxIteration_sb.value()
        nInit = self.uiplot.n_init_sb.value()
        k = self.uiplot.kNumber_sb.value()
        if self.uiplot.useInitCentroids_cb.isChecked() and self.kmeansClusterCenters is not None:
            self.kmeans = cluster.KMeans(k,  max_iter=maxIterations, n_init=nInit, init=self.kmeansClusterCenters)
        else:
            self.kmeans = cluster.KMeans(k,  max_iter=maxIterations, n_init=nInit)

        
    def learnKMeans(self):
        per = np.random.permutation(self.learnArrayKMeans)
        cluster_ = self.kmeans.fit_predict(per)
        #cluster_ = self.kmeans.kmeanstrain(self.learnArrayKMeans,maxIterations)
        #print self.learnArrayKMeans
        self.kMeansClassifier.setKMeans(self.kmeans)
        print 'learnKMeans : ', len(cluster_), '\n', cluster_
        #print 'cluster_.shape ', cluster_.shape
        self.kmeansClusterCenters =   self.kmeans.cluster_centers_

        
    def setMultipleFiles(self, value):
        self.multipleFiles = False if value == 0 else True

        
    def checkKMeans(self):
        self.checkOnline = not self.checkOnline
        self.kMeansClassifier.checkKMeansOnline()

        
    def testKMeans(self):
        class_  = self.kmeans.predict(self.learnArrayKMeans)
        print class_
        class_  = self.kmeans.transform(self.learnArrayKMeans[0])
        print class_.shape
        class_  = self.kmeans.score(self.learnArrayKMeans[0])
        print class_
    
    
    def setArarySidesCut(self):
        self.arraySidesCut = self.uiplot.cutSides_sb.value()
        self.idxLeft = self.arraySidesCut
        self.idxRight = self.sampleRate - self.arraySidesCut


    def addLogText(self, text1=None, text2=None, textColor='green'):
        newLine = str(text1) + '\n'
        if text2 is not None:
            newLine = str(text1) + str(text2) + '\n'
        self.globalLabelText = self.globalLabelText + newLine 
        self.textEdit.setTextColor(QColor(textColor))
        self.textEdit.setText(self.globalLabelText)
        self.textEdit.moveCursor(QtGui.QTextCursor.End)

        
    def callback(self, message, num):
        print 'message, num : ', message, num
    

    def loadCentroids(self):
        self.fileName = QtGui.QFileDialog.getOpenFileNames(self.win_plot, "Load centroids",
                self.centroidsFileDirectory, "*.kmeans")
        if len(self.fileName) == 0:
            self.addLogText('no file was chosen !', textColor='red')
            return
        elif len(self.fileName) > 1:
            self.addLogText('more than one file can''t be managed !', textColor='red')
            return
            
        path = str(self.fixpath(self.fileName[0]))        
        self.kmeansClusterCenters = np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))
        print 'self.kmeansClusterCenters.shape', self.kmeansClusterCenters.shape
         
        
    def saveCentroids(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self.win_plot, "Save centroids", self.centroidsFileDirectory, "*.kmeans")
        if len(fileName) == 0:
            self.addLogText('no name was given => no data is being saved !', textColor='red')
            return      
        oid = open(fileName, "a")
        # flatten all inputs to 1 vector
        print 'self.kmeansClusterCenters.shape',self.kmeansClusterCenters.shape 
        #segNormArray = self.kmH.reshapeArray3DTo2D64(self.segNormArray)
        data = np.array(self.kmeansClusterCenters)        
        np.savetxt(oid, data, delimiter=",")
        oid.close()        
      
      
    def bindButtons(self):
        self.uiplot.showPlot_bt.clicked.connect(self.showPlot)    
        self.uiplot.record_bt.clicked.connect(self.recordByRecorder)
        self.uiplot.openFile_bt.clicked.connect(self.openFile)
        self.uiplot.loadLearnArray_bt.clicked.connect(self.loadArrayFromFile)
        self.uiplot.showLearnArray_bt.clicked.connect(self.showGlobalViewArray)
        self.uiplot.arrayIdxLF_sb.valueChanged.connect(self.showGlobalViewArray)
        self.uiplot.skipFramesLA_sb.valueChanged.connect(self.showGlobalViewArray)
        ''' kmeans '''
        self.uiplot.initKMeans_bt.clicked.connect(self.initKMeans)
        self.uiplot.learnKMeans_bt.clicked.connect(self.learnKMeans)
        self.uiplot.checkKMeans_bt.clicked.connect(self.checkKMeans)
        self.uiplot.testKMeans_bt.clicked.connect(self.testKMeans)
        self.uiplot.saveCentorids_bt.clicked.connect(self.saveCentroids)
        self.uiplot.loadCentorids_bt.clicked.connect(self.loadCentroids)
        
        ''' classes buttons '''
        self.uiplot.class0_bt.clicked.connect(partial(self.segmentClasses, 0))
        self.uiplot.class1_bt.clicked.connect(partial(self.segmentClasses, 1))
        self.uiplot.class2_bt.clicked.connect(partial(self.segmentClasses, 2))
        self.uiplot.class3_bt.clicked.connect(partial(self.segmentClasses, 3))
        self.uiplot.class4_bt.clicked.connect(partial(self.segmentClasses, 4))
        self.uiplot.class5_bt.clicked.connect(partial(self.segmentClasses, 5))
        self.uiplot.class6_bt.clicked.connect(partial(self.segmentClasses, 6))
        self.uiplot.class7_bt.clicked.connect(partial(self.segmentClasses, 7))
        
        self.uiplot.cutSides_sb.valueChanged.connect(self.setArarySidesCut)
        self.uiplot.mulFiles_cb.stateChanged.connect(self.setMultipleFiles)       
        self.uiplot.saveFile_bt.clicked.connect(self.saveSegmentedData)
        self.uiplot.loadNoiseFile_bt.clicked.connect(self.loadNoiseFile)
        self.uiplot.reduceDim_bt.clicked.connect(self.reduceDimension)
        self.uiplot.viewCase1_rb.clicked.connect(partial(self.setViewCase, 1))
        self.uiplot.viewCase2_rb.clicked.connect(partial(self.setViewCase, 2))
        self.uiplot.viewCase3_rb.clicked.connect(partial(self.setViewCase, 3))
        self.uiplot.viewCase4_rb.clicked.connect(partial(self.setViewCase, 4))
        self.uiplot.perRatio_sb.valueChanged.connect(self.setPercentRatio)
        
        
    
    def setPercentRatio(self, value):
        self.kMeansClassifier.setPercentRatio(value)
        
    def loadNoiseFile(self):

        print QtCore.QDir.currentPath()
        self.fileName = QtGui.QFileDialog.getOpenFileNames(self.win_plot, "Load Noise File", "C:/Users/Robert/git/ml_soundwave_doppler_effect/gestures/Robert/gesture_7", "*.kmeans")

        paths = self.fileName
        if len(paths) == 0:
            self.addLogText('file open was canceled !')
            return 
        self.noiseArray = []     
        for idx, path in enumerate(paths):
            if idx == 0:
                self.noiseArray = np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))
            else:
                self.noiseArray = np.concatenate((self.noiseArray, np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))), axis=0)
        self.noiseArray = np.asarray(self.noiseArray)
        self.addLogText('noise array shape', self.noiseArray.shape)

    
    def reduceDimension(self):
        if len(self.arrayFromFile) == 0:
            self.addLogText('please add learn array at first !', textColor='red')
        elif len(self.noiseArray) == 0:
            self.addLogText('please add noise array at first !', textColor='red')
        
        elif self.arrayFromFile.shape[1] != self.noiseArray.shape[1]:
            self.addLogText('data and noise files do not have same shape', textColor='red')
            self.addLogText('noise shape', self.noiseArray.shape, textColor='red')
            self.addLogText('data shape', self.arrayFromFile.shape, textColor='red')
        else:
            #at first normalize noise data
            self.noiseArray = self.kmH.normalize3DArray(self.kmH.reshapeArray2DTo3D64(self.noiseArray))
            self.noiseArray = self.kmH.reshapeArray3DTo2D64(self.noiseArray)
            arrayToReduce = np.concatenate((self.arrayFromFile, self.noiseArray), axis=0)
            arrayToReduce =  self.kmH.reshapeArray2DTo3D64(arrayToReduce) 
            self.learnArrayKMeans = []
            for gesture in arrayToReduce:
                result = self.kmH.reduceDimensionality(gesture)
                if result is not None:
                    #print result.shape
                    result = np.asarray(result)
                    result = result.reshape(result.shape[0]*result.shape[1])

                    self.learnArrayKMeans.append(result)
                    #print result
                else:
                    self.addLogText('dupa')
            self.learnArrayKMeans = np.asarray(self.learnArrayKMeans)
            
            self.addLogText('reduce dimensionality finished !')
            self.addLogText('new dimension : !', self.learnArrayKMeans.shape )

        
    def saveSegmentedData(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self.win_plot, "Save reduced data", self.openFileDirectory, "*.kmeans")
        if len(fileName) == 0:
            self.addLogText('no name was given => no data is being saved !')
            return
        fNameSegNorm = fileName.replace(".kmeans","_seg_norm.kmeans")            
        oid = open(fNameSegNorm, "a")
        # flatten all inputs to 1 vector
        segNormArray = self.kmH.reshapeArray3DTo2D64(self.segNormArray)
        data = np.array(segNormArray)        
        np.savetxt(oid, data, delimiter=",")
        oid.close()
        fNameSegNormPlusSeg2K = fileName.replace(".kmeans","_seg_norm_2k.kmeans")            
        oid = open(fNameSegNormPlusSeg2K, "a")
        # flatten all inputs to 1 vector
        segNormArrayPlusSeg2K = self.kmH.reshapeArray3DTo2D64(self.preselectedByKMeansArray)
        data = np.array(segNormArrayPlusSeg2K)        
        np.savetxt(oid, data, delimiter=",")
        oid.close()
            
            
    def startNewThread(self):
        self.t = Thread(name="ControlGuiBob", target=self.start, args=())
        self.t.start()
        return self.t


    def is_alive(self):
        if self.t is not None:
            return self.t.is_alive()
        return False
   
   
    def start(self):
        # application
        self.app = QtGui.QApplication(sys.argv)

        self.win_plot = ui_kmeans_.QtGui.QMainWindow()
        
        self.win_plot.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        #
        self.uiplot = ui_kmeans_.Ui_MainWindow()
        self.uiplot.setupUi(self.win_plot)
        
        self.curve_tab1 = Qwt.QwtPlotCurve()
        self.curve_2_tab1 = Qwt.QwtPlotCurve()
        print 'geo : ', self.win_plot.geometry()
        desktop = self.app.desktop()
        res =  desktop.availableGeometry(desktop.primaryScreen());
        koor =  res.getCoords()
        print koor, (koor[2]/2-1378/2)/13, (koor[3]/2-740/2)/5
        self.win_plot.setGeometry(18, 33, 1378, 742)
        plot = self.uiplot
        print 'geo : ', self.win_plot.geometry()
        for i in range(1,33):

            qwtPlot = getattr(plot ,'qwtPlot_%d' %i)
            curr = getattr(self ,'curve_%d' %i)
        
            pen = Qt.QPen(Qt.Qt.red)
            pen.setStyle(1)
            pen.setWidth(1)
            curr.setPen(pen)
            
            curr.attach(qwtPlot)   
            self.curve_2_tab1 = Qwt.QwtPlotCurve()
            x1 = [32, 32]
            y1 = [0.0, 1000.0]
            self.curve_2_tab1.setData(x1, y1)
            
            pen = Qt.QPen(Qt.Qt.blue)
            pen.setStyle(1)
            pen.setWidth(1)
            self.curve_2_tab1.setPen(pen)

            self.curve_2_tab1.attach(qwtPlot)
            qwtPlot.setAxisScale(qwtPlot.yLeft, -100, self.amplitude * 1000)
        
        
        self.uiplot.timer = QtCore.QTimer()
        self.uiplot.timer.start(self.guiIntervall)

        self.win_plot.connect(self.uiplot.timer, QtCore.SIGNAL('timeout()'), self.plotSignal)
        
        self.arraySidesCut = self.uiplot.cutSides_sb.value()
        self.idxLeft = self.arraySidesCut
        self.idxRight = self.sampleRate - self.arraySidesCut
        

        
        self.bindButtons()
        self.kmH = kmHelper.kMeansHepler()   
        self.textEdit = QtGui.QTextEdit()
        self.uiplot.scrollArea.setWidget(self.textEdit)
        
        # ## DISPLAY WINDOWS
        self.win_plot.show()
       
        code = self.app.exec_()
        self.applicationClose(code)
       
           
#         sys.exit(code)
#         self.recorder.close()
    