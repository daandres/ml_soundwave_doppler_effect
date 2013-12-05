import ui_plot
import sys
from PyQt4 import QtCore, QtGui
import PyQt4.Qwt5 as Qwt
from numpy import array, shape, savetxt, ravel
import properties.config as config 
from numpy.f2py.auxfuncs import throw_error


class View:
     
    def __init__(self, recorder=None):
        # application
        self.app = None
        
        if recorder == None:
            raise Exception("No Recorder, so go home")
        self.recoder = recorder
        
        self.curve = None
        self.uiplot = None 
        # This will be decreased by one until 0 for recording 50 frames 
        self.recordNum = -1
        self.recordClass = -1
        self.ys_hist = []
        
        
    def record_0(self):
        self.recordClass = 0
        self.record()
    def record_1(self):
        self.recordClass = 1
        self.record()
    def record_2(self):
        self.recordClass = 2
        self.record()
    def record_3(self):
        self.recordClass = 3
        self.record()
    def record_4(self):
        self.recordClass = 4
        self.record()
    def record_5(self):
        self.recordClass = 5
        self.record()

    def stopRecording(self):
        print("Stop recording")
        if self.recordClass >= 0:
            self.writeGesture()
        else:
            self.cleanUp()    

    def cleanUp(self):
        self.status_btn_gesture(True)
        self.recordNum = -1
        self.recordClass = -1
        self.ys_hist = [] 

    def record(self):
        self.recordNum = config.recordingFrames
        self.status_btn_gesture(False)
            
    def status_btn_gesture(self, state):
        self.uiplot.btn_gesture_0.setEnabled(state)
        self.uiplot.btn_gesture_1.setEnabled(state)
        self.uiplot.btn_gesture_2.setEnabled(state)
        self.uiplot.btn_gesture_3.setEnabled(state)
        self.uiplot.btn_gesture_4.setEnabled(state)
        self.uiplot.btn_gesture_5.setEnabled(state)

    
    def plotSignal(self):
        xs, ys = self.recoder.getTransformedData()
        # somethin to record? 
        if(self.recordClass >= 0):
            if(self.recordNum > 0):
                self.recordData(ys)
            elif(self.recordNum == 0):
                self.writeGesture()    
            
        self.curve.setData(xs, ys) 
        self.uiplot.qwtPlot.replot() 
    
    def recordData(self, ys):
        self.recordNum -= 1
        self.ys_hist.append(ys)

    def writeGesture(self):
        outfile = config.gesturePath + "/gesture_" + str(self.recordClass) + ".txt"
        oid = open(outfile, "a")
        # oid.write("##### Class " + str(self.recordClass) + " #####\n")
        # flatten all inputs to 1 vector
        data = array([array(ravel(self.ys_hist))])
        print "Wrote record for class " + str(self.recordClass)
        savetxt(oid, data, delimiter=",", fmt='%1.4f')
        oid.close()
        self.cleanUp()

    def bindButtons(self):
        self.uiplot.btnPlot.clicked.connect(self.stopRecording)
        self.uiplot.btn_gesture_0.clicked.connect(self.record_0)
        self.uiplot.btn_gesture_1.clicked.connect(self.record_1)
        self.uiplot.btn_gesture_2.clicked.connect(self.record_2)
        self.uiplot.btn_gesture_3.clicked.connect(self.record_3)
        self.uiplot.btn_gesture_4.clicked.connect(self.record_4)
        self.uiplot.btn_gesture_5.clicked.connect(self.record_5)
            
    def start(self):    
        # application
        self.app = QtGui.QApplication(sys.argv)
    
        self.win_plot = ui_plot.QtGui.QMainWindow()
        self.uiplot = ui_plot.Ui_win_plot()
        self.uiplot.setupUi(self.win_plot)
    
        self.curve = Qwt.QwtPlotCurve()
        self.curve.attach(self.uiplot.qwtPlot)
    
        self.uiplot.qwtPlot.setAxisScale(self.uiplot.qwtPlot.yLeft, 0, 500)
    
        self.uiplot.timer = QtCore.QTimer()
        self.uiplot.timer.start(100.0)
    
    
        self.win_plot.connect(self.uiplot.timer, QtCore.SIGNAL('timeout()'), self.plotSignal)
        self.bindButtons()
        
        # ## DISPLAY WINDOWS
        self.win_plot.show()
        code = self.app.exec_()
        self.recoder.close()
        sys.exit(code)
