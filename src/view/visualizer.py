import ui_plot
import sys
from PyQt4 import QtCore, QtGui
import PyQt4.Qwt5 as Qwt
import properties.config as config 
from threading import Thread

class View:
     
    def __init__(self, recorder=None, applicationClose=None):
        # application
        self.app = None
        if recorder == None:
            raise Exception("No Recorder, so go home")
        self.recorder = recorder
        if applicationClose==None:
            raise Exception("No close callback")
        self.applicationClose = applicationClose
        self.curve = None
        self.uiplot = None 
        
    def callback(self, recClass):
        print "Recording finished for class " + str(recClass)
        self.status_btn_gesture(True)
        
    def record_0(self):
        self.recorder.setRecordClass(config.recordClass_0, self.callback)
    def record_1(self):
        self.recorder.setRecordClass(config.recordClass_1, self.callback)
    def record_2(self):
        self.recorder.setRecordClass(config.recordClass_2, self.callback)
    def record_3(self):
        self.recorder.setRecordClass(config.recordClass_3, self.callback)
    def record_4(self):
        self.recorder.setRecordClass(config.recordClass_4, self.callback)
    def record_5(self):
        self.recorder.setRecordClass(config.recordClass_5, self.callback)


    def record(self):
        self.status_btn_gesture(False)
  
    def plotSignal(self):
        data = self.recorder.getTransformedData()
        if data == None:
            return
        xs, ys = data
        self.curve.setData(xs, ys) 
        self.uiplot.qwtPlot.replot() 
                  
    def status_btn_gesture(self, state):
        self.uiplot.btn_gesture_0.setEnabled(state)
        self.uiplot.btn_gesture_1.setEnabled(state)
        self.uiplot.btn_gesture_2.setEnabled(state)
        self.uiplot.btn_gesture_3.setEnabled(state)
        self.uiplot.btn_gesture_4.setEnabled(state)
        self.uiplot.btn_gesture_5.setEnabled(state)

    def bindButtons(self):
        self.uiplot.btn_gesture_0.clicked.connect(self.record_0)
        self.uiplot.btn_gesture_1.clicked.connect(self.record_1)
        self.uiplot.btn_gesture_2.clicked.connect(self.record_2)
        self.uiplot.btn_gesture_3.clicked.connect(self.record_3)
        self.uiplot.btn_gesture_4.clicked.connect(self.record_4)
        self.uiplot.btn_gesture_5.clicked.connect(self.record_5)
            
    def startNewThread(self):
        self.t = Thread(name="ControlGui", target=self.start, args=())
        self.t.start()
        return self.t
    
    def is_alive(self):
        if self.t is not None:
            return self.t.is_alive()
        return False    
    
    def start(self):    
        # application
        self.app = QtGui.QApplication(sys.argv)
    
        self.win_plot = ui_plot.QtGui.QMainWindow()
        self.uiplot = ui_plot.Ui_win_plot()
        self.uiplot.setupUi(self.win_plot)
     
        self.curve = Qwt.QwtPlotCurve()
        self.curve.attach(self.uiplot.qwtPlot)
    
        self.uiplot.qwtPlot.setAxisScale(self.uiplot.qwtPlot.yLeft, 0, config.amplitude * 1000)
    
        self.uiplot.timer = QtCore.QTimer()
        self.uiplot.timer.start(config.guiIntervall)
    
    
        self.win_plot.connect(self.uiplot.timer, QtCore.SIGNAL('timeout()'), self.plotSignal)
        self.bindButtons()
        
        # ## DISPLAY WINDOWS
        self.win_plot.show()
        code = self.app.exec_()
        self.applicationClose(code)
        sys.exit(code)
#         self.recorder.close()
