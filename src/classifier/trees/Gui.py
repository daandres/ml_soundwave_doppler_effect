#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import Qt, QtCore, QtGui

'''
Simple gui to show an image for each gesutre.
'''
class Gui(QtGui.QWidget):

    newGesture = QtCore.pyqtSignal(int)

    def __init__(self, treeClassifier):
        self.classifier = treeClassifier
        self.classifier.newGesture.connect(self._receiveGesture)
        
        hbox = QtGui.QHBoxLayout(self)
        self.pixmap = QtGui.QPixmap("redrocks.jpg")

        lbl = QtGui.QLabel(self)
        lbl.setPixmap(self.pixmap)

        hbox.addWidget(lbl)
        self.setLayout(hbox)
        
        self.setWindowTitle('Red Rock')
        self.show()     
    
    
    @QtCore.pyqtSlot(int)
    def _receiveGesture(self, gesture):
        print gesture
        self.pixmap = QtGui.QPixmap("redrock.png")