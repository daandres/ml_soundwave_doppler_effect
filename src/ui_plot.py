# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_plot.ui'
#
# Created: Tue Nov 26 09:43:19 2013
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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
        self.btnA = QtGui.QPushButton(self.centralwidget)
        self.btnA.setObjectName(_fromUtf8("btnA"))
        self.horizontalLayout.addWidget(self.btnA)
        self.btnB = QtGui.QPushButton(self.centralwidget)
        self.btnB.setObjectName(_fromUtf8("btnB"))
        self.horizontalLayout.addWidget(self.btnB)
        self.btnC = QtGui.QPushButton(self.centralwidget)
        self.btnC.setObjectName(_fromUtf8("btnC"))
        self.horizontalLayout.addWidget(self.btnC)
        self.btnD = QtGui.QPushButton(self.centralwidget)
        self.btnD.setObjectName(_fromUtf8("btnD"))
        self.horizontalLayout.addWidget(self.btnD)
        self.verticalLayout.addLayout(self.horizontalLayout)
        win_plot.setCentralWidget(self.centralwidget)

        self.retranslateUi(win_plot)
        QtCore.QMetaObject.connectSlotsByName(win_plot)

    def retranslateUi(self, win_plot):
        win_plot.setWindowTitle(_translate("win_plot", "MainWindow", None))
        self.btnA.setText(_translate("win_plot", "A", None))
        self.btnB.setText(_translate("win_plot", "B", None))
        self.btnC.setText(_translate("win_plot", "C", None))
        self.btnD.setText(_translate("win_plot", "D", None))

from PyQt4 import Qwt5

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win_plot = QtGui.QMainWindow()
    ui = Ui_win_plot()
    ui.setupUi(win_plot)
    win_plot.show()
    sys.exit(app.exec_())

