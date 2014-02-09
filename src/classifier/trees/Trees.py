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
Implementation of tree classifier
'''
class Trees(IClassifier):

    def __init__(self, recorder=None, config=None, relative=""):
        self.name = "trees"
        self.config = config
        self.max_depth = int(self.config['max_depth'])
        self.estimators = int(self.config['estimators'])
        self.learning_rate = float(self.config['learning_rate'])
        gesture_ids = self.config['gestures'].split(',')
        self.gesture_ids = [int(x) for x in gesture_ids]
        self.queue_buffer = int(self.config['queue_buffer'])
        self.clf = GradientBoostingClassifier(n_estimators=self.estimators, max_depth=self.max_depth, learning_rate=self.learning_rate)
        self.data = []
        self.queue = deque()
        self.temp = deque()
        self.liste = []
        
        
        

    def getName(self):
        return self.name

    def startClassify(self):
        self.t = Thread(name=self.name, target=self.start, args=())
        self.t.start()
        return self.t

    def startTraining(self, args=[]):
        
        t = TrainingData(self.gesture_ids)
        gestures = t.getRawData()
        
        data = self.__preProcess(gestures)
        targets = t.getTargets()
 
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(data, targets, test_size=0.4, random_state=0)
        self.clf.fit(X_train, y_train)
        result = self.clf.predict(X_test) == y_test
        rightPredicts = len([x for x in result if x == True])
        print "Classifier is trained with", len(self.gesture_ids), "gestures: received ", 100. / len(result) * rightPredicts, "%"

    def classify(self, data):
        if(len(self.queue) == self.queue_buffer):
            gestures = []
            gesture = GestureModel(list(self.queue))
            gestures.append(gesture)
            processedData = self.__preProcess(gestures)
            self.temp.append(processedData)
            if(len(self.temp) == self.queue_buffer):
                recognizedGestures = []
                for item in list(self.temp):
                    prediction = self.clf.predict(item)
                    recognizedGestures.extend(prediction)
                result = numpy.argmax(numpy.bincount(recognizedGestures))
                if(result != 6):
                    print "Result: ", result
                
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
            
            featureVector.append(Feature().featureOrderOfShifts(gestures[i]))
            featureVector.append(Feature().featureConcurrentShifts(gestures[i], 2))
            featureVector.append(Feature().featureAmplitudes(gestures[i]))
            
            distance_contrary, distance_equal = Feature().shiftDistance(gestures[i])
            featureVector.append(distance_contrary)
            featureVector.append(distance_equal)
 
            gestures[i].featureVector = featureVector
            
            data.append(featureVector)
        return data
    
 
            