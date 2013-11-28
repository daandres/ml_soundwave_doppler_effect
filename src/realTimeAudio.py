import ui_plot
import sys
from PyQt4 import QtCore, QtGui
import PyQt4.Qwt5 as Qwt
from recorder import SwhRecorder
from numpy import array, shape
 
SR = None
c = None
uiplot = None 
# This will be decreased by one until 0 for recording 50 frames 
recordNum = 0
recordClass = -1
ys_hist = []


def init():
    def record_0():
        global recordClass
        recordClass = 0
        record()
    def record_1():
        global recordClass
        recordClass = 1
        record()
    def record_2():
        global recordClass
        recordClass = 2
        record()
    def record_3():
        global recordClass
        recordClass = 3
        record()
    def record_4():
        global recordClass
        recordClass = 4
        record()
    def record_5():
        global recordClass
        recordClass = 5
        record()

    def record():
        global recordNum
        recordNum = 50
        status_btn_gesture(False)
        
    def status_btn_gesture(state):
        uiplot.btn_gesture_0.setEnabled(state)
        uiplot.btn_gesture_1.setEnabled(state)
        uiplot.btn_gesture_2.setEnabled(state)
        uiplot.btn_gesture_3.setEnabled(state)
        uiplot.btn_gesture_4.setEnabled(state)
        uiplot.btn_gesture_5.setEnabled(state)

    
    def plotSomething():
        if SR.newAudio == False:
            return
        xs, ys = SR.fft()
        SR.newAudio = False
        if(recordNum > 0):
            recordData(ys)
        c.setData(xs, ys) 
        uiplot.qwtPlot.replot() 
    
    def recordData(ys):
        global ys_hist
        global recordNum
        ys_hist.append(ys)
        recordNum -= 1
        if(recordNum <= 0):
            status_btn_gesture(True)
            print "Class " + str(recordClass)
            print shape(array(ys_hist))
            ys_hist = []
        
    
    app = QtGui.QApplication(sys.argv)

    win_plot = ui_plot.QtGui.QMainWindow()
    uiplot = ui_plot.Ui_win_plot()
    uiplot.setupUi(win_plot)

    c = Qwt.QwtPlotCurve()
    c.attach(uiplot.qwtPlot)

    uiplot.qwtPlot.setAxisScale(uiplot.qwtPlot.yLeft, 0, 500)

    uiplot.timer = QtCore.QTimer()
    uiplot.timer.start(10.0)


    SR = SwhRecorder()
    SR.setup()
    SR.continuousStart()

    win_plot.connect(uiplot.timer, QtCore.SIGNAL('timeout()'), plotSomething)
    uiplot.btnPlot.clicked.connect(plotSomething)
    uiplot.btn_gesture_0.clicked.connect(record_0)
    uiplot.btn_gesture_1.clicked.connect(record_1)
    uiplot.btn_gesture_2.clicked.connect(record_2)
    uiplot.btn_gesture_3.clicked.connect(record_3)
    uiplot.btn_gesture_4.clicked.connect(record_4)
    uiplot.btn_gesture_5.clicked.connect(record_5)
    
    # ## DISPLAY WINDOWS
    win_plot.show()
    code = app.exec_()
    SR.close()
    sys.exit(code)
