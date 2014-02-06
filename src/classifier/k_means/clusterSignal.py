from PyQt4 import QtCore

class SignalToGUI(QtCore.QObject):

    currentGestureSignal = QtCore.pyqtSignal(int, name='rangeChanged')

    def __init__(self, parent=None):
        #super(SignalToGUI, self).__init__(parent)
        QtCore.QObject.__init__(self)
        #self.currentGetsure = -1

    def emitSignal(self, gesture):
        print 'ich emitiere !!'
        self.currentGestureSignal.emit(gesture)
