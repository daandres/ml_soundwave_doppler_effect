from PyQt4 import QtCore
class SignalToGUI(QtCore.QObject):
    #a pyqtSignal so we can get information in the GUI
    currentGestureSignal = QtCore.pyqtSignal(int, name='rangeChanged')

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self)

    def emitSignal(self, gesture):
        self.currentGestureSignal.emit(gesture)
    