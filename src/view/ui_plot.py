# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_plot.ui'
#
# Created: Thu Nov 28 11:31:01 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui,Qwt5

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_win_plot(object):
    def setupUi(self, win_plot):
        win_plot.setObjectName(_fromUtf8("win_plot"))
        win_plot.resize(800, 600)
        self.centralwidget = QtGui.QWidget(win_plot)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.qwtPlot = Qwt5.QwtPlot(self.centralwidget)
        self.qwtPlot.setObjectName(_fromUtf8("qwtPlot"))
        self.verticalLayout.addWidget(self.qwtPlot)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(6, 0, 6, 0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnPlot = QtGui.QPushButton(self.centralwidget)
        self.btnPlot.setObjectName(_fromUtf8("btnPlot"))
        self.horizontalLayout.addWidget(self.btnPlot)
        self.btn_gesture_0 = QtGui.QPushButton(self.centralwidget)
        self.horizontalLayout.addWidget(self.btn_gesture_0)
        self.btn_gesture_1 = QtGui.QPushButton(self.centralwidget)
        self.btn_gesture_1.setObjectName(_fromUtf8("btn_gesture_1"))
        self.horizontalLayout.addWidget(self.btn_gesture_1)
        self.btn_gesture_2 = QtGui.QPushButton(self.centralwidget)
        self.btn_gesture_2.setObjectName(_fromUtf8("btn_gesture_2"))
        self.horizontalLayout.addWidget(self.btn_gesture_2)
        self.btn_gesture_5 = QtGui.QPushButton(self.centralwidget)
        self.btn_gesture_5.setObjectName(_fromUtf8("btn_gesture_5"))
        self.horizontalLayout.addWidget(self.btn_gesture_5)
        self.btn_gesture_4 = QtGui.QPushButton(self.centralwidget)
        self.btn_gesture_4.setObjectName(_fromUtf8("btn_gesture_4"))
        self.horizontalLayout.addWidget(self.btn_gesture_4)
        self.btn_gesture_3 = QtGui.QPushButton(self.centralwidget)
        self.btn_gesture_3.setObjectName(_fromUtf8("btn_gesture_3"))
        self.horizontalLayout.addWidget(self.btn_gesture_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        win_plot.setCentralWidget(self.centralwidget)

        self.retranslateUi(win_plot)
        QtCore.QMetaObject.connectSlotsByName(win_plot)

    def retranslateUi(self, win_plot):
        win_plot.setWindowTitle(_translate("win_plot", "Soundwave gestures using Doppler Effect", None))
        self.btnPlot.setText(_translate("win_plot", "Plot fft", None))
        self.btn_gesture_0.setToolTip(_translate("win_plot", "Left-to-Right-One-Hand", None))
        self.btn_gesture_0.setText(_translate("win_plot", "Record 0", None))
        self.btn_gesture_1.setToolTip(_translate("win_plot", "Right-to-Left-One-Hand", None))
        self.btn_gesture_1.setText(_translate("win_plot", "Record 1", None))
        self.btn_gesture_2.setToolTip(_translate("win_plot", "Top-to-Bottom-One-Hand", None))
        self.btn_gesture_2.setText(_translate("win_plot", "Record 2", None))
        self.btn_gesture_5.setToolTip(_translate("win_plot", "Bottom-to-Top-One-Hand", None))
        self.btn_gesture_5.setText(_translate("win_plot", "Record 3", None))
        self.btn_gesture_4.setToolTip(_translate("win_plot", "Push-Two-Hands", None))
        self.btn_gesture_4.setText(_translate("win_plot", "Record 4", None))
        self.btn_gesture_3.setToolTip(_translate("win_plot", "Pull-Two-Hands", None))
        self.btn_gesture_3.setText(_translate("win_plot", "Record 5", None))

