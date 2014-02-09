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
        self.queue_buffer_len = int(self.config['queue_buffer_len'])
        
        self.data = []
        # frame buffer
        self.frame_buffer = deque()
        self.data_buffer = deque()
        
        # configure classifier
        self.clf = GradientBoostingClassifier(n_estimators=self.estimators, max_depth=self.max_depth, learning_rate=self.learning_rate)
        

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
 
        self.X_train, self.X_test, self.y_train, self.y_test = cross_validation.train_test_split(data, targets, test_size=0.5, random_state=0)
        self.clf.fit(self.X_train, self.y_train)
        print "Training: Classifier is trained with gestures", self.gesture_ids
        

    def classify(self, data):
        # collect defined number of frames and process the data in every step 
        # and append them to data_buffer
        if(len(self.frame_buffer) == self.queue_buffer_len):
            gestures = []
            gesture = GestureModel(list(self.frame_buffer))
            gestures.append(gesture)
            processedData = self.__preProcess(gestures)
            self.data_buffer.append(processedData)
            # collect defined number of data and predict every item of the queue
            if(len(self.data_buffer) == self.queue_buffer_len):
                recognizedGestures = []
                for item in list(self.data_buffer):
                    prediction = self.clf.predict(item)
                    recognizedGestures.extend(prediction)
                # calculate the frequent prediction
                result = numpy.argmax(numpy.bincount(recognizedGestures))
                if(result != 6):
                    print "Result: ", result
                
                self.data_buffer.clear()
            self.frame_buffer.popleft()
        self.frame_buffer.append(data)

    def startValidation(self):
        result = self.clf.predict(self.X_test) == self.y_test
        rightPredicts = len([x for x in result if x == True])
        print "Validation: Classifier received ", 100. / len(result) * rightPredicts, "%"

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
            # preprocess data
            relative = gestures[i].smoothRelative(gestures[i].bins_left_filtered, gestures[i].bins_right_filtered, 2)
            smoothed = gestures[i].smoothToMostCommonNumberOfBins(relative[0], relative[1], 1)
            gestures[i].bins_left_filtered, gestures[i].bins_right_filtered = gestures[i].combineNearPeaks(smoothed[0], smoothed[1])
            # order of shifts with direction, start, stop and max width
            shiftList = gestures[i].findShiftList()
            # order of shift directions ('right', 'left', 'both')
            shiftOrder = gestures[i].findShiftOrder(2, shiftList)
            
            # compute featureVector
            shifts_left, shifts_right = Feature().featureCountOfShifts(gestures[i], shiftList)
            featureVector.append(shifts_left + shifts_right)
            featureVector.append(shifts_left)
            featureVector.append(shifts_right)
            
            featureVector.append(Feature().featureOrderOfShifts(gestures[i], shiftList))
            featureVector.append(Feature().featureConcurrentShifts(gestures[i], 2, shiftOrder))
            featureVector.append(Feature().featureAmplitudes(gestures[i], shiftList))
            
            distance_contrary, distance_equal = Feature().shiftDistance(gestures[i], shiftList, shiftOrder)
            featureVector.append(distance_contrary)
            featureVector.append(distance_equal)
 
            data.append(featureVector)
        return data
    
 
            