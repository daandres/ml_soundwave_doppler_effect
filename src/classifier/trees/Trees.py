from classifier.classifier import IClassifier
from threading import Thread
from sklearn.ensemble import GradientBoostingClassifier
import classifier.trees.ProcessData
from classifier.trees.Feature import Feature
from classifier.trees.TrainingData import TrainingData
from classifier.trees.GestureModel import GestureModel
from collections import deque
import numpy
from sklearn import cross_validation
from PyQt4 import Qt, QtCore, QtGui
import sys


'''
QObject for signal
'''
class Signal(QtCore.QObject):
    
    newGesture = QtCore.pyqtSignal(int)
    def __init__(self, view):
        super(Signal, self).__init__()
        self.view = view # trees gui
        self.newGesture.connect(view._receiveGesture)

    
'''
Simple gui to show an image for each gesutre.
'''
class Gui(QtGui.QWidget):

    def __init__(self):
        super(Gui, self).__init__()
        
        hbox = QtGui.QHBoxLayout(self)
        self.pixmap = QtGui.QPixmap("C:/Users/Annalena/git/ml_soundwave_doppler_effect/src/classifier/trees/redrocks.jpg")

        lbl = QtGui.QLabel(self)
        lbl.setPixmap(self.pixmap)

        hbox.addWidget(lbl)
        self.setLayout(hbox)
        
        self.setWindowTitle('Red Rock')
        self.show()
    
    
    @QtCore.pyqtSlot(int)
    def _receiveGesture(self, gesture):
        print gesture


'''
Implementation of tree classifier
'''
class Trees(IClassifier):

    def __init__(self, recorder=None, n_est=5):
        self.name = "trees"
        self.maxlen = 32
        self.clf = GradientBoostingClassifier(n_estimators=50, max_depth=2, random_state=0)
        self.data = []
        self.queue = deque()
        self.temp = deque()
        self.startTraining()
        self.flag = False
        self.liste = []
        
        
        

    def getName(self):
        return self.name

    def startClassify(self):
        self.t = Thread(name=self.name, target=self.start, args=())
        self.t.start()
        return self.t

    def startTraining(self):
        
        #app = QtGui.QApplication(sys.argv)
        #self.gui = Gui()
        #self.signal = Signal(self.gui)
        #app.exec_()
        
        t = TrainingData()
        gestures = t.getRawData()
        
        data = self.__preProcess(gestures)
        targets = t.getTargets()
 
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(data, targets, test_size=0.4, random_state=0)
        self.clf.fit(X_train, y_train)
        result = self.clf.predict(X_test) == y_test
        rightPredicts = len([x for x in result if x == True])
        print "Classifier is trained: received ", 100. / len(result) * rightPredicts, "%"

    def classify(self, data):
        if(len(self.queue) == self.maxlen):
            gestures = []
            gesture = classifier.trees.ProcessData.makeGesture(list(self.queue))
            gestures.append(gesture)
            processedData = self.__preProcess(gestures)
            self.temp.append(processedData)
            if(len(self.temp) == self.maxlen):
                recognizedGestures = []
                for item in list(self.temp):
                    prediction = self.clf.predict(item)
                    recognizedGestures.extend(prediction)
                result = numpy.argmax(numpy.bincount(recognizedGestures))
                if(result != 6):
                    #print "Result: ", result
                    self.signal.newGesture.emit(result)
                
                self.temp.clear()
            self.queue.popleft()
        self.queue.append(data)

    def startValidation(self):
        pass

    def load(self, filename=""):
        pass

    def save(self, filename=""):
        pass

    def loadData(self, filename=""):
        pass        
            
    def saveData(self, filename=""):
        pass

    def printClassifier(self):
        pass
    
    def __preProcess(self, gestures):
        data = []
        for i in range(len(gestures)):
            featureVector = []
            relative = gestures[i].smoothRelative(gestures[i].bins_left_filtered, gestures[i].bins_right_filtered, 2)
            smoothed = gestures[i].smoothToMostCommonNumberOfBins(relative[0], relative[1], 1)
            gestures[i].bins_left_filtered, gestures[i].bins_right_filtered = gestures[i].combineNearPeaks(smoothed[0], smoothed[1])
            shifts_left, shifts_right = Feature().featureCountOfShifts(gestures[i])
            featureVector.append(shifts_left + shifts_right)
            featureVector.append(shifts_left)
            featureVector.append(shifts_right)
            
            featureVector.extend(Feature().featureOrderOfShifts(gestures[i], 2))
            featureVector.append(Feature().featureAmplitudes(gestures[i]))
            
            distance_contrary, distance_equal = Feature().shiftDistance(gestures[i])
            featureVector.append(distance_contrary)
            featureVector.append(distance_equal)
 
            gestures[i].featureVector = featureVector
            
            data.append(featureVector)
        return data
    
 
            