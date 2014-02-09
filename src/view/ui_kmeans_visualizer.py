import ui_kmeans as ui_kmeans_
import numpy as np

from PyQt4.QtCore import QObject, pyqtSlot, pyqtSignal
import sys, os
from PyQt4 import Qt, QtCore, QtGui
from PyQt4.QtGui import QMainWindow, QPushButton, QApplication
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *
from threading import Thread
import win32com.client
import copy
import ntpath
from functools import partial

from sklearn import cluster
import classifier.k_means.kMeansHelper as kmHelper
from properties.config import ConfigProvider
from PyQt4.Qt import QColor


class ViewUIKMeans:
    def __init__(self, kMeansClassifier=None, applicationClose=None, classSignal=None):

        self.kmH = None 
        self.kmeans = None
        self.kmeans_16N = None
        self.kmeansClusterCenters = None
        self.kmeansClusterCenters_16N = None
        self.arraySignal = np.array([]) 
        self.checkOnline = False

        self.idxLeft = 20
        self.idxRight = 44

        self.plot_id = 1
        self.framesToSkip = 1
        self.arraySidesCut = 0
       
        self.showRecords = False
        self.recordFramesCount = 32
        
        self.gesture0Aktiv, self.gesture1Aktiv, self.gesture3Aktiv, self.gesture4Aktiv = False, False, False, False
        
        if os.name == 'nt':
            self.isWindows = True
            self.shell = win32com.client.Dispatch("WScript.Shell")
        else:
            self.isWindows = False
            
        self.noiseArray = []
        self.arrayFromFile = []
        self.globalViewArray = []
        self.learnArrayKMeans = []
        self.arrayFromFileViewShape = []
        self.arrayFromFileViewShapeNorm = []
        self.preselectedByKMeansArray = []
        
        self.textEdit = None
        self.rightPage = None
        self.textBeginn = True
        self.akt = 1
        self.globalLabelText = 'Init!\n'
        self.segNormArray = []
        
        self.c0, self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7 = False, False, False, False, False, False, False, False
        self.showClusterList = [ self.c0, self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7 ]
        
        # xDummies
        self.xPoints = np.arange(64)
        
        self.fileName = None
        self.multipleFiles = False
        self.openFileDirectory = "../gestures/Robert"
        self.centroidsFileDirectory = "../gestures/Robert/Centroids/new/shape 24"
        self.app = None
        if kMeansClassifier == None:
            raise Exception("No kMeansClassifier, so go home")
        self.kMeansClassifier = kMeansClassifier
      
        self.newSignal = classSignal
        self.newSignal.currentGestureSignal.connect(self.setGestureTrigger)
        
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

     
    #toggle gesture icons depending on recognize gesture
    #set curve plot background red if recognizer busy with gesture  
    @pyqtSlot(int)
    def setGestureTrigger(self, gesture):
        if gesture == -10:
            self.uiplot.qwtPlot_page_1.setCanvasBackground(Qt.Qt.white)
        elif gesture == 10:
            self.uiplot.qwtPlot_page_1.setCanvasBackground(Qt.Qt.red)
        
        elif gesture == 0:
            if self.isWindows:
                #self.shell.SendKeys("{PGUP}",0)
                self.gesture0Aktiv = not self.gesture0Aktiv
                self.setGesturePixmap(gesture, self.gesture1Aktiv)
        
        elif gesture == 1:
            if self.isWindows:
                #self.shell.SendKeys("{PGDN}",0)
                self.gesture1Aktiv = not self.gesture1Aktiv
                self.setGesturePixmap(gesture, self.gesture1Aktiv)
         
        elif gesture == 3:
            self.gesture3Aktiv = not self.gesture3Aktiv
            self.setGesturePixmap(gesture, self.gesture3Aktiv)
            if self.akt < 5:
                self.akt +=1
            akt = str(self.akt) + '. Akt::'
            self.rightPage.scrollToAnchor('2')
    
        elif gesture == 4:
            self.gesture4Aktiv = not self.gesture4Aktiv
            self.setGesturePixmap(gesture, self.gesture4Aktiv)
            if self.textBeginn:
                self.textBeginn = False
                self.rightPage.scrollToAnchor('FINALE')
            else:
                self.textBeginn = True
                self.rightPage.scrollToAnchor('William Shakespeare:')
                self.akt = 1
        else:
            pass



    #aktivate live plot after viewing data from files    
    def showPlot(self):
        self.showRecords = False

    
    #get signal any tick of GUI timer and plot it
    #in main view the curve will replot any timer tick 
    #in second view the curve is refresh in roll way  
    def plotSignal(self):
        data = self.recorder.getTransformedData()
        if data == None:
            return
        xs, ys = data

        self.curve_page_1.setData(xs, ys) 
        self.uiplot.qwtPlot_page_1.replot()
                
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
            pass
            
    #start to buffer frame so we get data to recognition
    def recordByRecorder(self):
        self.recordFramesCount = self.uiplot.frames_sb.value()
        self.kMeansClassifier.fillBuffer(self.recordFramesCount)
        self.uiplot.record_bt.setStyleSheet('QPushButton {color: green}')
        
  
    #fixed the Windows/Unix path problem
    def fixpath(self, path):
        return path.replace('\\', '/')
                      
                        
    #main load data function
    #just get the file into a array
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
            for idx, path in enumerate(paths):
                if idx == 0:
                    self.arrayFromFile = np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))
                    self.addLogText('load array shape : ', self.arrayFromFile.shape, textColor='green')
                else:
                    self.arrayFromFile = np.concatenate((self.arrayFromFile, np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))), axis=0)
                    self.addLogText('load array shape : ', self.arrayFromFile.shape, textColor='green')
        else:
            for path in paths:
                if self.arrayFromFile == None:
                    self.arrayFromFile = np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))
                    self.addLogText('load array shape : ', self.arrayFromFile.shape, textColor='green')
                else:
                    self.arrayFromFile = np.concatenate((self.arrayFromFile, np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))), axis=0)
                    self.addLogText('load array shape : ', self.arrayFromFile.shape, textColor='green')

    

    #get the loaded array into right shape
    def loadArrayFromFile(self):
        arr = copy.copy(self.arrayFromFile)
        if len(arr) == 0:
            self.addLogText('you need to load a file before !', textColor='red')
            return
        self.addLogText('load files with shape', arr.shape)
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
        self.arrayFromFileViewShape = np.asarray(self.arrayFromFileViewShape)
        self.addLogText('view array shape', self.arrayFromFileViewShape.shape, textColor='green')
        self.arrayFromFileViewShapeNorm = self.kmH.normalize3DArray(self.arrayFromFileViewShape)        
        self.setGlobalViewArray(1)
   
    
    #get signal from GUI radio buttons and call the setGlobalViewArray funtion 
    def setViewCase(self, case, value ):
        yOrN = False if value == 0 else True
        if yOrN:
            self.setGlobalViewArray(case)
        
    #switch the array we want to view in the GUI 
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
        
    
    #iterate throw the array set by setGlobalViewArray and show the data as curve      
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
     
    #a preselect by kmeans with k=2
    def presortBy2Cluster(self, inArray):
        percent, cluster_, mode, kM = self.kmH.checkKMeansForSegmentation(inArray)
        b = cluster_ == mode
        return inArray[b]

    #chose the right segmentation way for the data and fill array with it
    def segmentClasses(self, classNumber ):
        classButton = getattr(self.uiplot,'class%d_bt' %classNumber)
        classButton.setStyleSheet('QPushButton {color: black; background-color: grey; font: bold;}')  
        arr = copy.copy(self.arrayFromFile) #shape (x, recordingFrames * 64) 
        if len(arr) == 0:
            self.addLogText('load data at first !', textColor='red')
            return
        frames = arr.shape[1]/64
        arr = arr.reshape(arr.shape[0],frames,64) #shape (x, recordingFrames, 64)
        #decide if is better
        arr = self.kmH.normalize3DArray(arr)
        endSegArray = []
        margin = self.uiplot.segMargin_sb.value()
        outLength = self.uiplot.frames_sb.value()
        for gesture in arr:
            segGesture = None
            if classNumber == 0:
                #right-To-Left-One-Hand
                #segGesture = self.kmH.segmentOneHandGesture(gesture, leftMargin=4, oneSecPeak=False)
                segGesture = self.kmH.segmentOneHandGesture(gesture, outArrayLength=outLength, leftMargin=margin, oneSecPeak=False)
            elif classNumber == 1:
                #top-to-Bottom-One-Hand
                #segGesture = self.kmH.segmentOneHandGesture(gesture, leftMargin=4, oneSecPeak=True)
                segGesture = self.kmH.segmentOneHandGesture(gesture, outArrayLength=outLength, leftMargin=margin, oneSecPeak=True)
            elif classNumber == 2:
                #opposed with two hands
                #segGesture = self.kmH.segmnetTwoHandsGesture(gesture, leftMargin=3)7
                segGesture = self.kmH.segmnetTwoHandsGesture(gesture, outArrayLength=outLength,  leftMargin=3)                            
            elif classNumber == 3:
                #single-push with one hand
                #segGesture = self.kmH.segmentOneHandGesture(gesture, leftMargin=4, oneSecPeak=False)
                segGesture = self.kmH.segmentOneHandGesture(gesture, outArrayLength=outLength, leftMargin=margin, oneSecPeak=False)
            elif classNumber == 4:
                #double-push with one hand #long period gesture so small left margin 
                #segGesture = self.kmH.segmentOneHandGesture(gesture, leftMargin=1, oneSecPeak=False)                
                segGesture = self.kmH.segmentOneHandGesture(gesture, outArrayLength=outLength, leftMargin=margin, oneSecPeak=False)
            elif classNumber == 6:
                #Bottom-to-top-One-Hand // changed for kmeans
                #segGesture = self.kmH.segmentOneHandGesture(gesture, leftMargin=4, oneSecPeak=True)
                segGesture = self.kmH.segmentOneHandGesture(gesture, outArrayLength=outLength, leftMargin=margin, oneSecPeak=True)                
            if segGesture is not None:
                endSegArray.append(segGesture)
            else:
                self.addLogText('segGesture == None')
        
        self.addLogText('segment class finished ! ')
        endSegArray = np.asarray(endSegArray)
        self.segNormArray = endSegArray
        self.addLogText('shape before preselect ', endSegArray.shape)        
        #check if a sort by two clusters help get better results
        self.preselectedByKMeansArray = self.presortBy2Cluster(self.kmH.reshapeArray3DTo2D64(endSegArray))
        self.preselectedByKMeansArray = np.asarray(self.preselectedByKMeansArray)
        self.preselectedByKMeansArray = self.kmH.reshapeArray2DTo3D64(self.preselectedByKMeansArray)
        self.addLogText('shape after preselect by 2 K', self.preselectedByKMeansArray.shape)

    #initialize kmeans by given settings from GUI
    def initKMeans(self):     
        maxIterations = self.uiplot.maxIteration_sb.value()
        nInit = self.uiplot.n_init_sb.value()
        k = self.uiplot.kNumber_sb.value()
        if self.uiplot.useInitCentroids_cb.isChecked() and self.kmeansClusterCenters is not None:
            self.kmeans = cluster.KMeans(k,  max_iter=maxIterations, n_init=nInit, init=self.kmeansClusterCenters)
            self.learnArrayKMeans = self.kmeansClusterCenters
        else:
            self.kmeans = cluster.KMeans(k,  max_iter=maxIterations, n_init=nInit)

    #learn kmeans with loaded data    
    def learnKMeans(self):
        if len(self.learnArrayKMeans) == 0:
            self.addLogText('you need at first load the learn set !', textColor='red')
            return
        if self.learnArrayKMeans.shape[0] < self.kmeans.n_clusters:
            self.addLogText('ValueError: n_samples=1 should be >= n_clusters=5', textColor='red')
            return  
        per = np.random.permutation(self.learnArrayKMeans)
        cluster_ = self.kmeans.fit_predict(per)
        self.kMeansClassifier.setKMeans(self.kmeans)
        self.addLogText('learn KMeans Count : ', len(cluster_))
        self.addLogText('cluster\n', cluster_)
        self.kmeansClusterCenters =   self.kmeans.cluster_centers_

    #switch the bool by depend on the GUI check box so we can load data from different directories      
    def setMultipleFiles(self, value):
        self.multipleFiles = False if value == 0 else True

    
    #activate online classification in the kMeans class     
    def checkKMeans(self):
        self.checkOnline = not self.checkOnline
        self.kMeansClassifier.checkKMeansOnline()


    #to avoid local minima execute the algorithm many time and compare the euklid distance between
    #the centroids at the end chose them with the greatest distance between the nearest one  
    def kMeansLoop(self):
        maxIterations = self.uiplot.maxIteration_sb.value()
        nInit = self.uiplot.n_init_sb.value()
        kLoop = self.uiplot.kMeansLoop_sb.value()
        k = self.uiplot.kNumber_sb.value()
        minDistance = 0.0
        for x in range(kLoop):
            if x == 0:
                self.kmeans = cluster.KMeans(k,  max_iter=maxIterations, n_init=nInit)
                if len(self.learnArrayKMeans) == 0:
                    self.addLogText('you need at first load the learn set !', textColor='red')
                    return
                if self.learnArrayKMeans.shape[0] < self.kmeans.n_clusters:
                    self.addLogText('ValueError: n_samples=1 should be >= n_clusters=5', textColor='red')
                    return  
                cluster_ = self.kmeans.fit_predict(self.learnArrayKMeans)
                self.kmeansClusterCenters =   self.kmeans.cluster_centers_
            else:
                self.kmeans = cluster.KMeans(k,  max_iter=maxIterations, n_init=nInit)
                cluster_ = self.kmeans.fit_predict(self.learnArrayKMeans)
                distanceList = []
                disIdxList = []
                for y in range(k):
                    for z in range(y+1,k):
                        distance = np.linalg.norm(self.kmeans.cluster_centers_[y] - self.kmeans.cluster_centers_[z])
                        #print int(distance)
                        distanceList.append(int(distance))
                        disIdxList.append([int(distance), y, z])                       
                distanceArray = np.asarray(distanceList)
                currDistance = np.amin(distanceArray)
                if currDistance > minDistance:
                    minDistance = currDistance
                    self.kmeansClusterCenters = self.kmeans.cluster_centers_
                    self.addLogText('current distance : ', currDistance)
        self.addLogText('repeated learning finished')
        self.addLogText('distance list\n', disIdxList)    
        
    
    #test the classifier by loaded data
    #the data isn't randomize, the sequence is given by load order,
    #so we can see the assignment with the naked eye
    def testKMeans(self):
        if self.kmeans is None or self.kmeansClusterCenters is None:
            self.addLogText('you need to init & learn kmeans at first!', textColor='red')
            return
        elif len(self.learnArrayKMeans) == 0:
            self.addLogText('load learn data at first !', textColor='red')
            return 
        elif self.kmeans.cluster_centers_.shape[1] != self.learnArrayKMeans.shape[1]:
            self.addLogText('cluster shape and data to test does''t matched !', textColor='red')
            self.addLogText('cluster shape : ', self.kmeans.cluster_centers_.shape)
            self.addLogText('loaded data shape :', self.learnArrayKMeans.shape)
            return 
        class_  = self.kmeans.predict(self.learnArrayKMeans)
        self.addLogText('classification by loaded array:\n', class_)
        class_  = self.kmeans.transform(self.learnArrayKMeans[0])
        #print class_.shape
        class_  = self.kmeans.score(self.learnArrayKMeans[0])
        self.addLogText('cluster score : ', class_)
    
    
    #set the indices for view array by GUI element
    def setArarySidesCut(self):
        self.arraySidesCut = self.uiplot.cutSides_sb.value()
        self.idxLeft = self.arraySidesCut
        self.idxRight = self.sampleRate - self.arraySidesCut

    #set any info output to the info label
    def addLogText(self, text1=None, text2=None, textColor='green'):
        newLine = str(text1) + '\n'
        if text2 is not None:
            newLine = str(text1) + str(text2) + '\n'
        self.globalLabelText = self.globalLabelText + newLine 
        self.textEdit.setTextColor(QColor(textColor))
        self.textEdit.setText(self.globalLabelText)
        self.textEdit.moveCursor(QtGui.QTextCursor.End)

    
    #load centroids from file 
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
        self.addLogText('kmeansClusterCenters shape : ', self.kmeansClusterCenters.shape)
    
         
    #save centroids to a file
    def saveCentroids(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self.win_plot, "Save centroids", self.centroidsFileDirectory, "*.kmeans")
        if len(fileName) == 0:
            self.addLogText('no name was given => no data is being saved !', textColor='red')
            return      
        oid = open(fileName, "a")
        # flatten all inputs to 1 vector
        self.addLogText('kmeansClusterCenters shape : ', self.kmeansClusterCenters.shape)
        data = np.array(self.kmeansClusterCenters)        
        np.savetxt(oid, data, delimiter=",")
        oid.close()        

        
    #main view button start recognition
    #load centroids and start recognition
    def startRecognition(self):
        if not self.checkOnline:
            self.checkOnline = not self.checkOnline
            self.uiplot.startRecognition_bt.setText('STOP RECOGNITION') 
            #self.kMeansClassifier.startTraining
            if self.kmeansClusterCenters is None:
                #default
                self.kmeansClusterCenters = np.asarray(np.loadtxt(str(self.fixpath("../gestures/Robert/Centroids/data/c_34N_k5_m4.kmeans")), delimiter=","))        
                self.addLogText('kmeansClusterCenters shape : ', self.kmeansClusterCenters.shape)  
            text=open("../gestures/Robert/Centroids/data/othello.kmeans").read()
            self.rightPage.setPlainText(text)        
            self.kmeans = cluster.KMeans(2,n_init=1,  init=self.kmeansClusterCenters)
            cluster_ = self.kmeans.fit_predict(self.kmeansClusterCenters)
            classArray = np.asarray(np.loadtxt(str(self.fixpath("../gestures/Robert/Centroids/data/classArray_34N.kmeans")), delimiter=","))
            self.kMeansClassifier.setClassArray(classArray)               
            self.kmeansClusterCenters_16N = np.asarray(np.loadtxt(str(self.fixpath("../gestures/Robert/Centroids/data/c_16N_m12_k3__.kmeans")), delimiter=","))
            self.kmeans_16N = cluster.KMeans(2,n_init=1,  init=self.kmeansClusterCenters_16N)
            cluster_ = self.kmeans_16N.fit_predict(self.kmeansClusterCenters_16N)
            self.kMeansClassifier.setKMeans(self.kmeans, self.kmeans_16N)
            self.recordByRecorder()
            self.kMeansClassifier.checkKMeansOnline() 
        else:
            self.uiplot.startRecognition_bt.setText('START RECOGNITION')
            self.checkOnline = not self.checkOnline
            self.kMeansClassifier.checkKMeansOnline()
      
      
    #just bind any GUI elements to intern function  
    def bindButtons(self):
        self.uiplot.startRecognition_bt.clicked.connect(self.startRecognition)
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
        self.uiplot.kMeansLoop_bt.clicked.connect(self.kMeansLoop)
        ''' classes buttons '''
        self.uiplot.class0_bt.clicked.connect(partial(self.segmentClasses, 0))
        self.uiplot.class1_bt.clicked.connect(partial(self.segmentClasses, 1))
        self.uiplot.class2_bt.clicked.connect(partial(self.segmentClasses, 2))
        self.uiplot.class3_bt.clicked.connect(partial(self.segmentClasses, 3))
        self.uiplot.class4_bt.clicked.connect(partial(self.segmentClasses, 4))
        self.uiplot.class5_bt.clicked.connect(partial(self.segmentClasses, 5))
        self.uiplot.class6_bt.clicked.connect(partial(self.segmentClasses, 6))
        self.uiplot.loadClassArray_bt.clicked.connect(self.loadClassArray)
        
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
        
    
    #load the array with the right class assignment
    def loadClassArray(self):
        classArray = self.loadFileToArray('class array', "../gestures/Robert/Centroids")
        self.addLogText('classArray shape ', classArray.shape)
        self.kMeansClassifier.setClassArray(classArray)
   

    #load noise data   
    def loadNoiseFile(self):
        self.noiseArray = self.loadFileToArray('noise array', "../gestures/Robert/gesture_7")
   
   
    #get the percent ratio from zhe GUI element    
    def setPercentRatio(self, value):
        self.kMeansClassifier.setPercentRatio(value)
       
       
    #generalized file to array funtion   
    def loadFileToArray(self, fileName, path):
        self.fileName = QtGui.QFileDialog.getOpenFileNames(self.win_plot, "Load " + fileName +"  file", path, "*.kmeans")
        paths = self.fileName
        if len(paths) == 0:
            self.addLogText('file open was canceled !')
            return 
        fileToArray= []     
        for idx, path in enumerate(paths):
            if idx == 0:
                fileToArray = np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))
            else:
                fileToArray = np.concatenate((fileToArray, np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))), axis=0)
        fileToArray = np.asarray(fileToArray)
        self.addLogText(fileName, fileToArray.shape)
        return fileToArray
        
        
    #reduce the data to desired dimension       
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
                result = self.kmH.reduceDimensionality(gesture, std='cut')
                if result is not None:
                    result = np.asarray(result)
                    self.learnArrayKMeans.append(result)
                else:
                    self.addLogText('not reducible')
            self.learnArrayKMeans = np.asarray(self.learnArrayKMeans)
            
            self.addLogText('reduce dimensionality finished !')
            self.addLogText('new dimension : !', self.learnArrayKMeans.shape )


    #save the segmented data to file    
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
            

    #new thread call            
    def startNewThread(self):
        self.t = Thread(name="ControlGui", target=self.start, args=())
        self.t.start()
        return self.t


    #thread callback
    def is_alive(self):
        if self.t is not None:
            return self.t.is_alive()
        return False


    #helper function to set the gesture icon 
    def setGesturePixmap(self, gesture, value):
        label = getattr(self.uiplot ,'gesture%d_lb' %gesture)
        icon = 'Icon0'+str(gesture)+'_aktiv.jpg' if value else 'Icon0'+str(gesture)+'.jpg'
        iconPath = "../gestures/Robert/Centroids/data/"+icon
        icon1 = QtGui.QPixmap(iconPath)
        icon1 = icon1.scaled(100, 100)
        label.setPixmap(icon1) 
   
   
    #end of application 
    def end(self):
        self.uiplot.timer.Stop(self.guiIntervall)
   
   
    #set all initial parameter with the start of the apllication    
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
        
        self.win_plot.setGeometry(18, 33, 1366, 780)
        
        self.curve_page_1 = Qwt.QwtPlotCurve()
        self.curve_page_1.attach(self.uiplot.qwtPlot_page_1)       
        self.uiplot.qwtPlot_page_1.setAxisScale(self.uiplot.qwtPlot_page_1.yLeft, 0, self.amplitude * 1000)
        plot = self.uiplot
        
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
        

        self.setGesturePixmap(0, False)
        self.setGesturePixmap(1, False)
        self.setGesturePixmap(3, False)
        self.setGesturePixmap(4, False)
        
        self.bindButtons()
        self.kmH = kmHelper.kMeansHepler()
        self.textEdit = QtGui.QTextEdit()
        self.uiplot.scrollArea.setWidget(self.textEdit)
        
        self.rightPage = QtGui.QTextEdit()
        self.rightPage.setFont(QtGui.QFont ("Courier", 16));
        self.uiplot.rightPage_sa.setWidget(self.rightPage)
        

        # ## DISPLAY WINDOWS
        self.win_plot.show()
        code = self.app.exec_()
        return code

    
