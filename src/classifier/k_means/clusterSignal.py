from PyQt4 import QtCore
import numpy as np
class SignalToGUI(QtCore.QObject):

    currentGestureSignal = QtCore.pyqtSignal(int, name='rangeChanged')
    #currentFrame = QtCore.pyqtSignal(np.array([]), name='rangeChanged')

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self)

    def emitSignal(self, gesture):
        self.currentGestureSignal.emit(gesture)
    '''
    def emitFrame(self, frame):
        self.currentFrame.emit(frame)
    '''