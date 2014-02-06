from PyQt4 import QtCore

class SignalToGUI(QtCore.QObject):

    currentGestureSignal = QtCore.pyqtSignal(int, name='rangeChanged')

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self)

    def emitSignal(self, gesture):
        self.currentGestureSignal.emit(gesture)
