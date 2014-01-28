import ui_bob_ as ui_bob
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

import classifier.k_means.kMeans_Helper as kmHelper

from sklearn import cluster, svm 

import copy

from classifier.k_means.kMeans_Helper import CallbackMessage
    
    


class ViewUIBob:
    def __init__(self, recorder=None, applicationClose=None):
    #def __init__(self, applicationClose=None):
        
        self.cm = CallbackMessage()
        self.callbackButton = None
        self.calibrationBarValue = 0
        self.recordsBarValue = 0
        
        self.ratateArrayIdx = 0
        self.rotateArrayBool = False
        
        
        self.kmH = None 
        
        self.kmeans = None
        
        self.checkOnline = False
        
        self.toogleClass0 = False
        self.toogleClass1 = False
        self.toogleClass2 = False
        self.toogleClass3 = False
        self.toogleClass4 = False
        self.toogleClass5 = False
        self.toogleClass6 = False
        self.toogleClass7 = False
        
        self.kmeansClusterCenters = None
        self.kmeansClusterCentersNumber = 0
        
        self.arraySidesCut = 0
        self.idxLeft = 20
        self.idxRight = 44
        
        self.perCent = 0.0
        
        self.picToRecordArray = []
        
        self.segmentArray = []
        self.picArray = False
        
        self.plot_id = 1
        self.initCalArray = []
        self.calibMean = []
        self.initCalibration = False
        self.gestureArray = []
        self.recordArray = []
        self.recordFramesCount = 32
        self.framesToSkip = 1
        self.record = False
        self.showRecords = False
        self.fileName = None
        
        self.calSampCount = 0
        self.calibSampleList = []
        
        self.learnArray = []
        self.learnArrayKMeans = []
        
        self.arrayFromFile = []
        self.multipleFiles = False
        
        self.gestureFrameCount = 32
        self.calibratetSignal = False
        self.plotBinaryCurve = False
        
        self.bufferedPlot = False
        
        self.c0, self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7 = False, False, False, False, False, False, False, False
        self.showClusterList = [ self.c0, self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7 ]
        
        self.xPoints = np.array([ 17742.1875, 17765.625,   17789.0625,  17812.5  ,   17835.9375,  17859.375,
                                  17882.8125, 17906.25 ,   17929.6875,  17953.125,   17976.5625,  18000.   ,
                                  18023.4375, 18046.875,   18070.3125,  18093.75 ,   18117.1875,  18140.625,
                                  18164.0625, 18187.5  ,   18210.9375,  18234.375,   18257.8125,  18281.25 ,
                                  18304.6875, 18328.125,   18351.5625,  18375.   ,   18398.4375,  18421.875,
                                  18445.3125, 18468.75 ,   18492.1875,  18515.625,   18539.0625,  18562.5  ,
                                  18585.9375, 18609.375,   18632.8125,  18656.25 ,   18679.6875,  18703.125,
                                  18726.5625, 18750.   ,   18773.4375,  18796.875,   18820.3125,  18843.75 ,
                                  18867.1875, 18890.625,   18914.0625,  18937.5  ,   18960.9375,  18984.375,
                                  19007.8125, 19031.25 ,   19054.6875,  19078.125,   19101.5625,  19125.   ,
                                  19148.4375, 19171.875,   19195.3125,  19218.75  ])
        
        # application
        
        self.openFileDirectory = "C:/Users/Bob/git/ml_soundwave_doppler_effect/gestures/Robert/gesture_0"
        
        
        self.app = None
        if recorder == None:
            raise Exception("No Recorder, so go home")
        self.recorder = recorder
        
        if applicationClose == None:
            raise Exception("No close callback")
        self.applicationClose = applicationClose
       
        self.uiplot_tab1, self.curve_tab1 = None, None
        self.curve_2_tab1 = None
        '''
        self.curve_1 , self.curve_2 , self.curve_3 , self.curve_4 , self.curve_5 , self.curve_6 , self.curve_7 ,self.curve_8 = None,None,None,None,None,None,None,None
        self.curve_9 ,self.curve_10 ,self.curve_11 ,self.curve_12 ,self.curve_13 ,self.curve_14 , self.curve_15 , self.curve_16 = None,None,None,None,None,None,None,None
        self.curve_17 , self.curve_18 , self.curve_19 , self.curve_20 , self.curve_21 , self.curve_22 , self.curve_23 , self.curve_24 = None,None,None,None,None,None,None,None
        self.curve_25 , self.curve_26 ,self.curve_27 ,self.curve_28 ,self.curve_29 ,self.curve_30 ,self.curve_31 ,self.curve_32 = None,None,None,None,None,None,None,None         
        '''
        
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

    def setCurveForOnlinePlot(self):
        self.showRecords = True
        plot = self.uiplot
        curveListCp = copy.copy(self.curveList)
        for i in range(1,32):

            qwtPlot = getattr(plot ,'qwtPlot_%d' %i)
            curr = curveListCp[i-1]
            #curr = Qwt.QwtPlotCurve()#copy.copy(cur)
            #curr.setPen({color: green} )
            #curr.setStyle(Qwt.QwtPlotCurve.Dots)
            
            pen = Qt.QPen(Qt.Qt.red)
            pen.setStyle(1)
            pen.setWidth(1)
            curr.setPen(pen)
            
            curr.attach(qwtPlot)   
            self.curve_2_tab1 = Qwt.QwtPlotCurve()
            x1 = [18500.0, 18500.0]
            y1 = [0.0, 1000.0]
            self.curve_2_tab1.setData(x1, y1)
            
            pen = Qt.QPen(Qt.Qt.blue)
            pen.setStyle(1)
            pen.setWidth(1)
            self.curve_2_tab1.setPen(pen)



            self.curve_2_tab1.attach(qwtPlot)
            qwtPlot.setAxisScale(qwtPlot.yLeft, -100, self.amplitude * 1000)
        self.showRecords = False
            
        for i in range (1,33):
            data = self.recorder.getTransformedData()
            if data == None:
                return
            xs, ys = data
           
            
            ys = ys[self.idxLeft:self.idxRight]
            xs = xs[self.idxLeft:self.idxRight]
        
            i = self.plot_id
            qwtPlot = getattr(self.uiplot ,'qwtPlot_%d' %i)
            curr = getattr(self ,'curve_%d' %i)
            self.plot_id = self.plot_id +1
            
            curr.setData(xs, ys)
            qwtPlot.replot()
            
            if self.plot_id == 33:
                self.plot_id = 1
        
            if self.checkOnline:
                self.toogleForClass()
            
            
    def plotSignal(self):
        self.uiplot.calibration_pb.setValue(self.calibrationBarValue)
        self.uiplot.records_pb.setValue(self.recordsBarValue)
        data = self.recorder.getTransformedData()
        if data == None:
            return
        xs, ys = data
       
        if self.plotBinaryCurve:
            ys = self.frameBinaryByPeak(ys, 'none')
     
        
        ys = ys[self.idxLeft:self.idxRight]
        xs = xs[self.idxLeft:self.idxRight]
        
        if not self.showRecords:
            if self.bufferedPlot:
                recArray = copy.copy( self.recorder.getBuffer())
                for i in range (1,33):
                    
                    qwtPlot = getattr(self.uiplot ,'qwtPlot_%d' %i)
                    curr = getattr(self ,'curve_%d' %i)
                    ii = i-1
                    ys = recArray[ii]

                    curr.setData(xs, ys)
                    qwtPlot.replot()
            else:    
                i = self.plot_id
                qwtPlot = getattr(self.uiplot ,'qwtPlot_%d' %i)
                curr = getattr(self ,'curve_%d' %i)
                self.plot_id = self.plot_id +1
                
                curr.setData(xs, ys)
                qwtPlot.replot()
                
                if self.plot_id == 33:
                    self.plot_id = 1
        '''
        if self.checkOnline:
            self.toogleForClass()
        ''' 
   
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
    
    def initialCalibration(self):
        self.uiplot.calibration_bt.setStyleSheet('QPushButton {color: yellow}')     
        self.recordFramesCount = self.uiplot.initCalibration_sb.value()
        self.recorder.initialCalibration(self.recordFramesCount, self.callback)
        
    def getCalibrationData(self, yData):
        if(self.calSampCount > 0):
            if yData == None:
                self.uiplot.calibration_bt.setStyleSheet('QPushButton {color: red}')
                return
            self.calibSampleList.append(yData)
            self.calSampCount = self.calSampCount - 1
            #print self.calSampCount
        else:
            self.initCalArray = np.asarray(self.calibSampleList)
            print self.initCalArray.shape
            self.calibMean = np.mean( self.initCalArray, axis=0)
            print self.calibMean.shape
            self.initCalibration = False
            self.uiplot.calibration_bt.setStyleSheet('QPushButton {color: green}')
             
    
    def calibration(self):
        #self.calibratetSignal = not self.calibratetSignal
        self.recorder.calibrateSignal()
        
    def binaryPlot(self):
        self.plotBinaryCurve = not self.plotBinaryCurve
        
    def recordByRecorder(self):
        self.recordsBarValue = 0
        self.uiplot.record_bt.setStyleSheet('QPushButton {color: yellow}')
        
        self.recordFramesCount = self.uiplot.frames_sb.value()
        self.recorder.fillBuffer(self.recordFramesCount, self.callback)
        self.uiplot.record_bt.setStyleSheet('QPushButton {color: green}')
        
        
        
    def recordTest(self):
        self.uiplot.record_bt.setStyleSheet('QPushButton {color: yellow}')
        self.recordArray = []
        self.recordFramesCount = self.uiplot.frames_sb.value()
        self.record = True
    
    def recordFrames(self, yData):
        if(self.recordFramesCount > 0):
            if yData == None:
                self.uiplot.record_bt.setStyleSheet('QPushButton {color: red}')
                return
            self.recordArray.append(yData)
            self.recordFramesCount = self.recordFramesCount - 1
        else:
            self.record = False
            self.uiplot.record_bt.setStyleSheet('QPushButton {color: green}')
    
    def showRecordByRecorder(self):
        self.recordArray = copy.copy( self.recorder.getBuffer())
        xs, yshit  = self.recorder.getTransformedData()
        xs = xs[self.idxLeft:self.idxRight]
        
        self.uiplot.skipFrames_sb.setStyleSheet('QSpinBox {color: green}')
        self.showRecords = True
        self.framesToSkip = self.uiplot.skipFrames_sb.value()
        showAny = self.uiplot.showAnyX_sb.value()
        
        if ((self.framesToSkip+32) > len(self.recordArray)):
            self.framesToSkip = 0
            self.uiplot.skipFrames_sb.setStyleSheet('QSpinBox {color: red}')
        for i in range (1,33):
            #print i
            qwtPlot = getattr(self.uiplot ,'qwtPlot_%d' %i)
            curr = getattr(self ,'curve_%d' %i)
            ii = i-1
            ys = self.recordArray[ii*showAny + self.framesToSkip]
            '''
            if self.calibratetSignal:
                ys = ys - self.calibMean
            ''' 
            if self.plotBinaryCurve:
                ys = self.frameBinaryByPeak(ys, none)
                      
           
            
            curr.setData(xs, ys)
            qwtPlot.replot()
        
    def showRecord(self):
        self.uiplot.skipFrames_sb.setStyleSheet('QSpinBox {color: green}')
        self.showRecords = True
        self.framesToSkip = self.uiplot.skipFrames_sb.value()
        showAny = self.uiplot.showAnyX_sb.value()
        
        if ((self.framesToSkip+32) > len(self.recordArray)):
            self.framesToSkip = 0
            self.uiplot.skipFrames_sb.setStyleSheet('QSpinBox {color: red}')
        for i in range (1,33):
            print i
            qwtPlot = getattr(self.uiplot ,'qwtPlot_%d' %i)
            curr = getattr(self ,'curve_%d' %i)
                        
            curr.setData(self.xPoints, self.recordArray[i*showAny + self.framesToSkip])
            qwtPlot.replot()
    
    def showPlot(self):
        self.setCurveForOnlinePlot()
        #self.showRecords = False
        
    def frameBinaryByPeak(self, frame, perCent):
        newMaxV = 500
        maxV = np.amax(frame)
        maxP = np.argmax(frame)
        
        result = copy.copy(frame)
        result[maxP] = newMaxV   
        
        for x in xrange(len(frame)):
            result[x] = (float(int((frame[x] / frame[maxP])*100)))/100*newMaxV
        result[maxP] = newMaxV
        '''      
        for i in range(maxP, len(frame)-1):
            if frame[i+1] < frame[i]:
                result[i+1] = 0
            else:
                result[i+1] = (float(int((frame[i+1] / frame[maxP])*10)))/10*newMaxV  
        for i in range(maxP, 0, -1):
            if frame[i-1] < frame[i]:
                result[i-1] = 0
            else:
                result[i-1] = (float(int((frame[i-1] / frame[maxP])*10)))/10*newMaxV
        '''
        return result
        
    def openFile(self):
        print QtCore.QDir.currentPath()
        self.fileName = QtGui.QFileDialog.getOpenFileNames(self.win_plot, "Open ",
                self.openFileDirectory, "*.txt")
        ppath = str(self.fixpath(self.fileName[0]))
        print ppath
        path = ntpath.dirname(ppath)
        print path
        self.openFileDirectory = path
        #self.getArrayFromFile(str(self.fixpath(self.fileName[0])))
        #path = str(self.fixpath(self.fileName[0]))
        paths = self.fileName
       
        if not self.multipleFiles:        
            for idx, path in enumerate(paths):
                if idx == 0:
                    self.arrayFromFile = np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))
                else:
                    self.arrayFromFile = np.concatenate((self.arrayFromFile, np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))), axis=0)
        else:
            for path in paths:
                if self.arrayFromFile == None:
                    self.arrayFromFile = np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))
                    print 'direct path: ', self.arrayFromFile.shape
                else:
                    self.arrayFromFile = np.concatenate((self.arrayFromFile, np.asarray(np.loadtxt(str(self.fixpath(path)), delimiter=","))), axis=0)
                    print 'direct path: ', self.arrayFromFile.shape
        #self.getArrayFromFile()
        
    def fixpath(self, path):
        return path.replace('\\', '/')
    
    def loadArrayFromFile(self):
        arr = copy.copy(self.arrayFromFile)
        print arr.shape
        if len(arr.shape) == 1:
            self.learnArrayKMeans = arr.reshape((1,arr.shape))
            frames = arr.shape/64
            arr = arr.reshape((1, frames, 64))
            self.learnArray = np.asarray(arr)
            self.learnArrayKMeans = arr.reshape((1,arr.shape))
        else:
            '''
            if self.plotBinaryCurve:
                lowValY = self.uiplot.binaryPlot_dsb.value()
                for x in xrange(arr.shape[0]):
                    tmpA = arr[x]
                    maX = np.amax(tmpA)
                    lvidx = tmpA < lowValY*maX  # Where values are low
                    tmpA[lvidx] = 0.0 
                    hvidx = tmpA > lowValY*maX  # Where values are height
                    tmpA[hvidx] = 500.0 
            ''' 
             
            
            frames = arr.shape[1]/64
            arr = arr.reshape(arr.shape[0],frames,64)
            self.learnArray = np.asarray(arr)
            print 'shape', arr.shape
            
            ''' xxx ''' '''  
            
            if self.plotBinaryCurve:
                for x in xrange(arr.shape[0]):
                    for y in xrange(arr.shape[1]):
                        self.learnArray[x][y]= self.frameBinaryByPeak(self.learnArray[x][y], self.perCent )
                        
           
            self.learnArray = self.learnArray[::,::,0:self.learnArray.shape[2]:self.framesToSkip]
            
            kMeansArray = self.learnArray[::,::,self.idxLeft:self.idxRight]
            
            
            self.learnArrayKMeans = kMeansArray.reshape(kMeansArray.shape[0],32*((self.idxRight-self.idxLeft)/self.framesToSkip),)
            ''' ''' xxx '''
            self.learnArrayKMeans = []
            self.segmentArray = []
            for x in xrange(arr.shape[0]):
                #print 'arr[x].shape', arr[x].shape
                outBoolArray =  self.kmH.segmentInputData(arr[x], 16, .15, 10, normalize=True)
                
                if outBoolArray is not None:
                    self.segmentArray.append(outBoolArray)
                    #print 'outBoolArray.shape ', outBoolArray.shape
                    result = self.kmH.reduceDimensionality(outBoolArray)
                    if result is not None:
                        #print result.shape
                        result = np.asarray(result)
                        result = result.reshape(result.shape[0]*result.shape[1])
                        #self.learnArray.append(result)
                        self.learnArrayKMeans.append(result)
                        print result
                else:
                    print 'array empty !!!'
                
                
       
        self.learnArrayKMeans = np.asarray(self.learnArrayKMeans)
        self.learnArray = self.learnArrayKMeans
        print 'k-means learn phase finish !'
        print self.learnArray.shape
        print self.learnArrayKMeans.shape
        
        self.segmentArray = np.asarray(self.segmentArray)
           
   
    def showArrayFromFile(self):
        self.uiplot.arrayIdxLF_sb.setStyleSheet('QSpinBox {color: green}')
        self.showRecords = True
        rAIdx = self.uiplot.arrayIdxLF_sb.value()
        skipFrames = self.uiplot.skipFramesLA_sb.value()
        
        if (rAIdx > self.learnArray.shape[0]-1):
            rAIdx = 0
            self.uiplot.arrayIdxLF_sb.setStyleSheet('QSpinBox {color: red}')
            rAIdx = self.uiplot.arrayIdxLF_sb.setValue(0)
        print self.learnArray[rAIdx].shape

        ''' xxx '''
        
        if self.rotateArrayBool:
            aTMP = np.roll(self.segmentArray[rAIdx], self.framesToSkip, axis=0)
        else:
            aTMP = self.segmentArray[rAIdx][skipFrames:(skipFrames+32)]
                
        if self.picArray:
            
                
            print 'aTMP ', aTMP.shape
            aTMP = aTMP.reshape(2048)
            print 'aTMP ', aTMP.shape
            self.picToRecordArray.append(aTMP)
            aa = np.asarray(self.picToRecordArray)
            print aa.shape
            self.picArray = False
        print self.segmentArray.shape
        for i in range (0,self.segmentArray.shape[1]):
            ii = i+1
            qwtPlot = getattr(self.uiplot ,'qwtPlot_%d' %ii)
            curr = getattr(self ,'curve_%d' %ii)
            
            ys = aTMP[i]#self.learnArray[rAIdx][i+skipFrames]
            ys = ys[self.idxLeft:self.idxRight]
            xs = self.xPoints[self.idxLeft:self.idxRight]
                       
            curr.setData(xs, ys)
            qwtPlot.replot()
     
    def showRecordBinary(self, value):
        self.perCent = value
        print value
        '''
        if self.showRecords:
            self.showRecordByRecorder()
        '''
        
    def initKMeans(self):
        maxIterations = self.uiplot.maxIteration_sb.value()
        k = self.uiplot.kNumber_sb.value()
        self.kmeans = cluster.KMeans(k,  max_iter=maxIterations)
        #self.kmeans = kmeans(k, self.learnArrayKMeans)
        
    def learnKMeans(self):
        maxIterations = self.uiplot.maxIteration_sb.value()
        per = np.random.permutation(self.learnArrayKMeans)
        cluster_ = self.kmeans.fit_predict(per)
        #cluster_ = self.kmeans.kmeanstrain(self.learnArrayKMeans,maxIterations)
        #print self.learnArrayKMeans
        self.recorder.setKMeans(self.kmeans, self.uiplot.binaryPlot_dsb.value(), self.perCent)
        print 'learnKMeans : ', len(cluster_), '\n', cluster_
        #print 'cluster_.shape ', cluster_.shape
        self.kmeansClusterCenters =   self.kmeans.cluster_centers_
        
    def setMultipleFiles(self, value):
        self.multipleFiles = False if value == 0 else True
        
    def checkKMeans(self):
        self.checkOnline = not self.checkOnline
        self.recorder.checkKMeansOnline()
        
    def testKMeans(self):
        result = 0.
        for x in xrange(self.learnArrayKMeans.shape[0]):
            twice = [self.learnArrayKMeans[x]]
            #class_  = self.kmeans.kmeansfwd(twice)
            #result = result + (self.learnArrayKMeans[x][0] - class_)
            #print x, self.learnArrayKMeans[x][0]
        
        #print 'result : ', result   
  
        class_  = self.kmeans.predict(self.learnArrayKMeans)
        print class_
    
    def setArarySidesCut(self):
        self.arraySidesCut = self.uiplot.cutSides_sb.value()
        self.idxLeft = self.arraySidesCut
        self.idxRight = self.sampleRate - self.arraySidesCut
        #self.recorder.setArraySidesCut(self.idxLeft, self.idxRight)


    def setBufferedPlot(self):
        self.bufferedPlot = not self.bufferedPlot
        
    def callback(self, message, num):
        print 'message, num : ', message, num
      
    def bindButtons(self):
        self.uiplot.initCalibration_bt.clicked.connect(self.initialCalibration)
        self.uiplot.calibration_bt.clicked.connect(self.calibration)
        self.uiplot.binaryPlot_bt.clicked.connect(self.binaryPlot)
        self.uiplot.record_bt.clicked.connect(self.recordByRecorder)
        #self.uiplot.record_bt.clicked.connect(self.recordTest)
        self.uiplot.showRecord_bt.clicked.connect(self.showRecordByRecorder)
        #self.uiplot.showRecord_bt.clicked.connect(self.showRecord)
        self.uiplot.skipFrames_sb.valueChanged.connect(self.showRecordByRecorder)
        
        self.uiplot.skipFrames_sb_2.valueChanged.connect(self.skipFramesLearn)
        
        self.uiplot.showPlot_bt.clicked.connect(self.showPlot)
        self.uiplot.showAnyX_sb.valueChanged.connect(self.showRecordByRecorder)
        self.uiplot.openFile_bt.clicked.connect(self.openFile)
        self.uiplot.loadLearnArray_bt.clicked.connect(self.loadArrayFromFile)
        
        self.uiplot.showLearnArray_bt.clicked.connect(self.showArrayFromFile)
        self.uiplot.arrayIdxLF_sb.valueChanged.connect(self.showArrayFromFile)
        self.uiplot.skipFramesLA_sb.valueChanged.connect(self.showArrayFromFile)
        
        self.uiplot.binaryPlot_dsb.valueChanged.connect(self.showRecordBinary)
        
        '''kmeans'''
        self.uiplot.initKMeans_bt.clicked.connect(self.initKMeans)
        self.uiplot.learnKMeans_bt.clicked.connect(self.learnKMeans)
        self.uiplot.checkKMeans_bt.clicked.connect(self.checkKMeans)
        self.uiplot.testKMeans_bt.clicked.connect(self.testKMeans)
    
        self.uiplot.cutSides_sb.valueChanged.connect(self.setArarySidesCut)
        self.uiplot.mulFiles_cb.stateChanged.connect(self.setMultipleFiles)
        self.uiplot.bufferedPlot_rb.clicked.connect(self.setBufferedPlot)
        
        self.uiplot.saveFile_bt.clicked.connect(self.savePickedArray)
        self.uiplot.picToRecordArray_bt.clicked.connect(self.picToRecArray)
        
        self.uiplot.showCluster_bt.clicked.connect(self.showClusterCenters)

        
        self.uiplot.c0_cb.stateChanged.connect(partial(self.setClusterList, 0))
        self.uiplot.c1_cb.stateChanged.connect(partial(self.setClusterList, 1))
        self.uiplot.c2_cb.stateChanged.connect(partial(self.setClusterList, 2))
        self.uiplot.c3_cb.stateChanged.connect(partial(self.setClusterList, 3))
        self.uiplot.c4_cb.stateChanged.connect(partial(self.setClusterList, 4))
        self.uiplot.c5_cb.stateChanged.connect(partial(self.setClusterList, 5))
        self.uiplot.c6_cb.stateChanged.connect(partial(self.setClusterList, 6))
        self.uiplot.c7_cb.stateChanged.connect(partial(self.setClusterList, 7))
        
        self.uiplot.rotArray_cb.stateChanged.connect(self.setRotateArrayBool)
        self.uiplot.rotateArray_sb.valueChanged.connect(self.setRotateArrayIdx)
    
    def setRotateArrayIdx(self, value):
        self.ratateArrayIdx = value
        
    def setRotateArrayBool(self, value):
        self.rotateArrayBool = False if value == 0 else True
    
    def skipFramesLearn(self, value):
        self.framesToSkip = value    
         
    def setClusterList(self, cluster, value ):
        # x if cond else y
        print 'y/n : ', False if value == 0 else True
        yOrN = False if value == 0 else True
        self.showClusterList[cluster] = yOrN
        print 'setClusterList ',value, cluster
        self.showClusterCenters()
    
    def showClusterCenters(self):
        
        self.showRecords = True
        clusterArray = copy.copy(self.kmeansClusterCenters)
        print 'clusterArray ', clusterArray.shape
        clusterArray = clusterArray.reshape(clusterArray.shape[0],32,((self.idxRight-self.idxLeft)/self.framesToSkip))
        print 'clusterArray ', clusterArray.shape

        print self.learnArray.shape
        plot = self.uiplot
        
        ''' clear '''
        for i in range (0,32):
            ii = i+1
            qwtPlot = getattr(plot ,'qwtPlot_%d' %ii)
            qwtPlot._plotdict={}
            qwtPlot.clear()
            qwtPlot.replot()
            
        for x in xrange(clusterArray.shape[0]):
            if self.showClusterList[x]:           
                for i in range (0,32):
                    ii = i+1
                    qwtPlot = getattr(plot ,'qwtPlot_%d' %ii)
                    self.curve_2_tab1 = Qwt.QwtPlotCurve()
                    xs = self.xPoints[self.idxLeft:self.idxRight]
                    ys = clusterArray[x][i]
                    self.curve_2_tab1.setData(xs, ys)
                    
                    pen = Qt.QPen(self.getButtonColor(x, button=False))
                    pen.setStyle(1)
                    pen.setWidth(1)
                    self.curve_2_tab1.setPen(pen)
                    self.curve_2_tab1.attach(qwtPlot)
    
                    qwtPlot.replot()

    def picToRecArray(self):
        self.picArray = True
        self.showArrayFromFile()
        
    def savePickedArray(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self.win_plot, "Save Array", self.openFileDirectory, "*.txt")
                      
        oid = open(fileName, "a")
        # flatten all inputs to 1 vector
        data = np.array(self.picToRecordArray)        
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

        self.win_plot = ui_bob.QtGui.QMainWindow()
        self.uiplot = ui_bob.Ui_MainWindow()
        self.uiplot.setupUi(self.win_plot)
        
        self.curve_tab1 = Qwt.QwtPlotCurve()
        self.curve_2_tab1 = Qwt.QwtPlotCurve()
        '''
        self.curve_1, self.curve_2, self.curve_3, self.curve_4, self.curve_5, self.curve_6, self.curve_7, self.curve_8 = Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()
        self.curve_9, self.curve_10, self.curve_11, self.curve_12, self.curve_13, self.curve_14, self.curve_15, self.curve_16 = Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()
        self.curve_17, self.curve_18, self.curve_19, self.curve_20, self.curve_21, self.curve_22, self.curve_23, self.curve_24 = Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()
        self.curve_25, self.curve_26, self.curve_27, self.curve_28, self.curve_29, self.curve_30, self.curve_31, self.curve_32 = Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()
        '''
        plot = self.uiplot
        
        for i in range(1,33):

            qwtPlot = getattr(plot ,'qwtPlot_%d' %i)
            curr = getattr(self ,'curve_%d' %i)
            #curr = Qwt.QwtPlotCurve()
            #curr.setPen({color: green} )
            #curr.setStyle(Qwt.QwtPlotCurve.Dots)
            
            pen = Qt.QPen(Qt.Qt.red)
            pen.setStyle(1)
            pen.setWidth(1)
            curr.setPen(pen)
            
            curr.attach(qwtPlot)   
            self.curve_2_tab1 = Qwt.QwtPlotCurve()
            x1 = [18500.0, 18500.0]
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
        
        self.perCent = self.uiplot.binaryPlot_dsb.value()
        
        self.bindButtons()
        
        self.kmH = kmHelper.kMeansHepler()
        
        xs, ys  = self.recorder.getTransformedData()
        
        print 'xs shape ', xs.shape 
        print xs
        print xs[0]-xs[1]
            
        
        # ## DISPLAY WINDOWS
        self.win_plot.show()
       
        code = self.app.exec_()
        self.applicationClose(code)
       
           
#         sys.exit(code)
#         self.recorder.close()
    