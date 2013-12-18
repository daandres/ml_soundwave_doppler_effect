# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_plot.ui'
#
# Created: Wed Dec 18 16:04:37 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui, Qwt5

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
        self.qwtPlot.setEnabled(False)
        self.qwtPlot.setObjectName(_fromUtf8("qwtPlot"))
        self.verticalLayout.addWidget(self.qwtPlot)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(6, 0, 6, 0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btn_gesture_0 = QtGui.QPushButton(self.centralwidget)
        self.btn_gesture_0.setEnabled(True)
        self.btn_gesture_0.setCheckable(False)
        self.btn_gesture_0.setAutoRepeat(False)
        self.btn_gesture_0.setObjectName(_fromUtf8("btn_gesture_0"))
        self.horizontalLayout.addWidget(self.btn_gesture_0)
        self.btn_gesture_1 = QtGui.QPushButton(self.centralwidget)
        self.btn_gesture_1.setObjectName(_fromUtf8("btn_gesture_1"))
        self.horizontalLayout.addWidget(self.btn_gesture_1)
        self.btn_gesture_2 = QtGui.QPushButton(self.centralwidget)
        self.btn_gesture_2.setObjectName(_fromUtf8("btn_gesture_2"))
        self.horizontalLayout.addWidget(self.btn_gesture_2)
        self.btn_gesture_3 = QtGui.QPushButton(self.centralwidget)
        self.btn_gesture_3.setObjectName(_fromUtf8("btn_gesture_3"))
        self.horizontalLayout.addWidget(self.btn_gesture_3)
        self.btn_gesture_4 = QtGui.QPushButton(self.centralwidget)
        self.btn_gesture_4.setObjectName(_fromUtf8("btn_gesture_4"))
        self.horizontalLayout.addWidget(self.btn_gesture_4)
        self.btn_gesture_5 = QtGui.QPushButton(self.centralwidget)
        self.btn_gesture_5.setObjectName(_fromUtf8("btn_gesture_5"))
        self.horizontalLayout.addWidget(self.btn_gesture_5)
        self.btn_gesture_6 = QtGui.QPushButton(self.centralwidget)
        self.btn_gesture_6.setObjectName(_fromUtf8("btn_gesture_6"))
        self.horizontalLayout.addWidget(self.btn_gesture_6)
        self.btn_gesture_7 = QtGui.QPushButton(self.centralwidget)
        self.btn_gesture_7.setObjectName(_fromUtf8("btn_gesture_7"))
        self.horizontalLayout.addWidget(self.btn_gesture_7)
        self.verticalLayout.addLayout(self.horizontalLayout)
        win_plot.setCentralWidget(self.centralwidget)

        self.retranslateUi(win_plot)
        QtCore.QMetaObject.connectSlotsByName(win_plot)

    def retranslateUi(self, win_plot):
        win_plot.setWindowTitle(_translate("win_plot", "Soundwave gestures using Doppler Effect", None))
        self.btn_gesture_0.setToolTip(_translate("win_plot", "Right-To-Left-One-Hand", None))
        self.btn_gesture_0.setText(_translate("win_plot", "Record 0", None))
        self.btn_gesture_1.setToolTip(_translate("win_plot", "Top-to-Bottom-One-Hand", None))
        self.btn_gesture_1.setText(_translate("win_plot", "Record 1", None))
        self.btn_gesture_2.setToolTip(_translate("win_plot", "Entgegengesetzt with two hands", None))
        self.btn_gesture_2.setText(_translate("win_plot", "Record 2", None))
        self.btn_gesture_3.setToolTip(_translate("win_plot", "Single-push with one hand", None))
        self.btn_gesture_3.setText(_translate("win_plot", "Record 3", None))
        self.btn_gesture_4.setToolTip(_translate("win_plot", "Double-push with one hand", None))
        self.btn_gesture_4.setText(_translate("win_plot", "Record 4", None))
        self.btn_gesture_5.setToolTip(_translate("win_plot", "Rotate one hand", None))
        self.btn_gesture_5.setText(_translate("win_plot", "Record 5", None))
        self.btn_gesture_6.setToolTip(_translate("win_plot", "Background noise (no gesture, but in silent room)", None))
        self.btn_gesture_6.setText(_translate("win_plot", "Record 6", None))
        self.btn_gesture_7.setToolTip(_translate("win_plot", "No gesture with background sound (in a Pub, at office, in the kitchen, etc.)", None))
        self.btn_gesture_7.setText(_translate("win_plot", "Record 7", None))
