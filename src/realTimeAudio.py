import ui_plot
import sys
from PyQt4 import QtCore, QtGui
import PyQt4.Qwt5 as Qwt
from recorder import SwhRecorder
from numpy import array, shape
 


class View:
     

    def __init__(self):
        # application
        self.app = None
        
        self.recoder = None
        self.curve = None
        self.uiplot = None 
        # This will be decreased by one until 0 for recording 50 frames 
        self.recordNum = 0
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

    def record(self):
        self.recordNum = 50
        self.status_btn_gesture(False)
            
    def status_btn_gesture(self, state):
        self.uiplot.btn_gesture_0.setEnabled(state)
        self.uiplot.btn_gesture_1.setEnabled(state)
        self.uiplot.btn_gesture_2.setEnabled(state)
        self.uiplot.btn_gesture_3.setEnabled(state)
        self.uiplot.btn_gesture_4.setEnabled(state)
        self.uiplot.btn_gesture_5.setEnabled(state)

    
    def plotSignal(self):
        if self.recoder.getNewAudio() == False:
            return
        xs, ys = self.recoder.fft()
        self.recoder.setNewAudio = False
        if(self.recordNum > 0):
            self.recordData(ys)
        self.curve.setData(xs, ys) 
        self.uiplot.qwtPlot.replot() 
    
    def recordData(self, ys):
        self.ys_hist.append(ys)
        self.recordNum -= 1
        if(self.recordNum <= 0):
            self.status_btn_gesture(True)
            print "Class " + str(self.recordClass)
            print shape(array(self.ys_hist))
            self.ys_hist = []

    def bindButtons(self):
        self.uiplot.btnPlot.clicked.connect(self.plotSignal)
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
        self.uiplot.timer.start(10.0)
    
    
        self.recoder = SwhRecorder()
        self.recoder.setup()
        self.recoder.continuousStart()
    
        self.win_plot.connect(self.uiplot.timer, QtCore.SIGNAL('timeout()'), self.plotSignal)
        self.bindButtons()
        
        # ## DISPLAY WINDOWS
        self.win_plot.show()
        code = self.app.exec_()
        self.recoder.close()
        sys.exit(code)
