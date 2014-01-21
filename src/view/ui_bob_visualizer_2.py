import ui_bob
import numpy as np

import sys, os
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMainWindow, QPushButton, QApplication
import PyQt4.Qwt5 as Qwt
from threading import Thread
from properties.config import ConfigProvider
import time

#from classifier.k_means.kMeans import kmeans

import copy


class CallbackMessage():
    bufferFilled = 1
    progress = 2 
    
    
    


class ViewUIBob:
    def __init__(self, recorder=None, applicationClose=None):
    #def __init__(self, applicationClose=None):
        
        self.cm = CallbackMessage()
        self.callbackButton = None
        self.calibrationBarValue = 0
        self.recordsBarValue = 0
        
        self.kmeans = None
        
        self.plot_id = 1
        self.initCalArray = []
        self.calibMean = []
        self.initCalibration = False
        self.gestureArray = []
        self.recordArray = []
        self.recordFramesCount = 32
        self.framesToSkip = 0
        self.record = False
        self.showRecords = False
        self.fileName = None
        
        self.calSampCount = 0
        self.calibSampleList = []
        
        self.learnArray = []
        
        self.gestureFrameCount = 32
        self.calibratetSignal = False
        self.plotBinaryCurve = False
        
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
        
        self.app = None
        

       
        self.uiplot_tab1, self.curve_tab1 = None, None
        self.curve_2_tab1 = None
       
        self.curve_1 , self.curve_2 , self.curve_3 , self.curve_4 , self.curve_5 , self.curve_6 , self.curve_7 ,self.curve_8 = None,None,None,None,None,None,None,None
        self.curve_9 ,self.curve_10 ,self.curve_11 ,self.curve_12 ,self.curve_13 ,self.curve_14 , self.curve_15 , self.curve_16 = None,None,None,None,None,None,None,None
        self.curve_17 , self.curve_18 , self.curve_19 , self.curve_20 , self.curve_21 , self.curve_22 , self.curve_23 , self.curve_24 = None,None,None,None,None,None,None,None
        self.curve_25 , self.curve_26 ,self.curve_27 ,self.curve_28 ,self.curve_29 ,self.curve_30 ,self.curve_31 ,self.curve_32 = None,None,None,None,None,None,None,None         
        

    
   
        
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
        self.showRecords = False
        
    def openFile(self):
        print QtCore.QDir.currentPath()
        self.fileName = QtGui.QFileDialog.getOpenFileNames(self.win_plot, "Open ",
                "C:/Users/Bob/git/ml_soundwave_doppler_effect/gestures/Robert/gesture_0", "*.txt")
        self.getArrayFromFile(str(self.fixpath(self.fileName[0])))

    def fixpath(self, path):
        return path.replace('\\', '/')
    
    def getArrayFromFile(self, path):
        arr = np.loadtxt(path, delimiter=",")
        
        if len(arr.shape) == 1:
            frames = arr.shape/64
            arr = arr.reshape((1, frames, 64))
            self.learnArray = np.asarray(arr)
        else:
            frames = arr.shape[1]/64
            arr = arr.reshape(arr.shape[0],frames,64)
            self.learnArray = np.asarray(arr)
             
        print self.learnArray.shape
   
    def loadLearnArray(self):
        self.uiplot.arrayIdxLF_sb.setStyleSheet('QSpinBox {color: green}')
        self.showRecords = True
        rAIdx = self.uiplot.arrayIdxLF_sb.value()
        skipFrames = self.uiplot.skipFramesLA_sb.value()
        
        if (rAIdx > self.learnArray.shape[0]-1):
            rAIdx = 0
            self.uiplot.arrayIdxLF_sb.setStyleSheet('QSpinBox {color: red}')
            rAIdx = self.uiplot.arrayIdxLF_sb.setValue(0)
        for i in range (0,32):
            ii = i+1
            qwtPlot = getattr(self.uiplot ,'qwtPlot_%d' %ii)
            curr = getattr(self ,'curve_%d' %ii)
            
            ys = self.learnArray[rAIdx][i+skipFrames]
            
            if self.calibratetSignal:
                ys = ys - self.calibMean
            
            if self.plotBinaryCurve:
                #dVec = np.asarray(ys)
                lowValY = self.uiplot.binaryPlot_dsb.value()
                lvidx = ys < lowValY  # Where values are low
                ys[lvidx] = 0.0 
                hvidx = ys > lowValY  # Where values are height
                ys[hvidx] = 500.0 
                        
            curr.setData(self.xPoints, ys)
            qwtPlot.replot()
     
    def showRecordBinary(self):
        if self.showRecords:
            self.showRecordByRecorder()
       
    def initKMeans(self):
        k = self.uiplot.kNumber_sb.value()
        maxIteration = self.uiplot.maxIteration_sb.value()
        #self.k
        
    def learnKMeans(self):
        print 'learnMeans'
        
    def checkKMeans(self):
        print 'checkMeans'
        
    
    def callback(self, message, num):
        
        if message == 0:
            print '0'
            
        elif message == 1:
            self.recordsBarValue = 100
        elif message == 2:
            self.calibrationBarValue = num
            self.uiplot.calibration_bt.setStyleSheet('QPushButton  {color: green} ')
              
    def bindButtons(self):




        #self.uiplot.record_bt.clicked.connect(self.recordTest)

        #self.uiplot.showRecord_bt.clicked.connect(self.showRecord)

        self.uiplot.showPlot_bt.clicked.connect(self.showPlot)

        self.uiplot.openFile_bt.clicked.connect(self.openFile)
        self.uiplot.loadLearnArray_bt.clicked.connect(self.loadLearnArray)
        self.uiplot.arrayIdxLF_sb.valueChanged.connect(self.loadLearnArray)
        self.uiplot.skipFramesLA_sb.valueChanged.connect(self.loadLearnArray)
        
        self.uiplot.binaryPlot_dsb.valueChanged.connect(self.showRecordBinary)
        
        '''kmeans'''
        self.uiplot.initKMeans_bt.clicked.connect(self.initKMeans)
        self.uiplot.learnKMeans_bt.clicked.connect(self.learnKMeans)
        self.uiplot.checkKMeans_bt.clicked.connect(self.checkKMeans)
    
    
        
        
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
        
        self.curve_1, self.curve_2, self.curve_3, self.curve_4, self.curve_5, self.curve_6, self.curve_7, self.curve_8 = Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()
        self.curve_9, self.curve_10, self.curve_11, self.curve_12, self.curve_13, self.curve_14, self.curve_15, self.curve_16 = Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()
        self.curve_17, self.curve_18, self.curve_19, self.curve_20, self.curve_21, self.curve_22, self.curve_23, self.curve_24 = Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()
        self.curve_25, self.curve_26, self.curve_27, self.curve_28, self.curve_29, self.curve_30, self.curve_31, self.curve_32 = Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()
        




       
      
        
        plot = self.uiplot

        for i in range(1,33):

            qwtPlot = getattr(plot ,'qwtPlot_%d' %i)
            curr = getattr(self ,'curve_%d' %i)
            #curr.setPen({color: green} )
            #curr.setStyle(Qwt.QwtPlotCurve.Dots)
            curr.attach(qwtPlot)    
            qwtPlot.setAxisScale(qwtPlot.yLeft, -100, 1 * 1000)
        
        
        self.uiplot.timer = QtCore.QTimer()
        self.uiplot.timer.start(2)

        #self.win_plot.connect(self.uiplot.timer, QtCore.SIGNAL('timeout()'), self.plotSignal)
        
        
        
        self.bindButtons()
        
    
            

        # ## DISPLAY WINDOWS
        self.win_plot.show()
       
        code = self.app.exec_()
        self.applicationClose(code)
       
           
#         sys.exit(code)
#         self.recorder.close()


if __name__ == '__main__':
    try:
#         printHelp()
        app = ViewUIBob()
        app.start()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        exitApp()
    