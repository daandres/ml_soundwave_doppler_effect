from classifier.classifier import IClassifier
from threading import Thread
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
import classifier.trees.ProcessData
from classifier.trees.Feature import Feature
from classifier.trees.GestureModel import GestureModel
from collections import deque
import numpy
from sklearn import cross_validation
import matplotlib.pyplot as plt



class Trees(IClassifier):

    def __init__(self, recorder=None, n_est=5):
        self.name = "trees"
        self.maxlen = 32
        self.clf = GradientBoostingClassifier(n_estimators=50, max_depth=2, random_state=0)
        self.data = []
        self.queue = deque()
        self.temp = deque()
        self.startTraining()

    def getName(self):
        return self.name

    def startClassify(self):
        self.t = Thread(name=self.name, target=self.start, args=())
        self.t.start()
        return self.t

    def startTraining(self):
        #gestures = classifier.trees.ProcessData.getTestData("../gestures/Daniel/gesture_2/1387660041_fernsehen.txt")
        #gestures += classifier.trees.ProcessData.getTestData("../gestures/Daniel/gesture_3/1387647860_zimmer_left.txt")
        #gestures += classifier.trees.ProcessData.getTestData("../gestures/Daniel/gesture_4/1387647860_zimmer_left.txt")
        #gestures += classifier.trees.ProcessData.getTestData("../gestures/Daniel/gesture_6/gesture_6_zimmer_1.txt")
        
        gestures = classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_2/1391437451.txt")
        gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_2/1391437809.txt")
        gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_3/1391439011.txt")
        gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_3/1391439281.txt")
        gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_4/1391439536.txt")
        gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_4/1391439659.txt")
        gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_0/1391435081.txt")
        gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_0/1391435669.txt")
        gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_1/1391436572.txt")
        gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_1/1391436738.txt")
        gestures += classifier.trees.ProcessData.getTestData("../gestures/Daniel/gesture_6/gesture_6_zimmer_1.txt")
        gestures += classifier.trees.ProcessData.getTestData("../gestures/Daniel/gesture_6/gesture_6_zimmer_3.txt")
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
            #l = []
            #l.extend(gestures[i].bins_left_filtered)
            #l.extend(gestures[i].bins_right_filtered)
            #l.extend(gestures[i].featureVector)
            #data.append(l)
            
            data.append(featureVector)
 
        targets = []
        for class_ in [2,2,3,3,4,4,0,0,1,1,6,6]:
            for frameIndex in range(50):
                targets.append(class_)
        #print numpy.shape(data)
        #print numpy.shape(targets)
        #X_train, X_test, y_train, y_test = cross_validation.train_test_split(data2, targets, test_size=0.4, random_state=0)
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(data, targets, test_size=0.4, random_state=0)
        self.clf.fit(X_train, y_train)
        #self.clf.fit(data, targets)
        result = self.clf.predict(X_test) == y_test
        rightPredicts = len([x for x in result if x == True])
        print 100. / len(result) * rightPredicts
        print "trained"


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
        gestures = classifier.trees.ProcessData.getTestData(filename)
        self.__preProcess(gestures)
        print "loadData"
        
            
    def saveData(self, filename=""):
        pass

    def printClassifier(self):
        # von jedem estimator den baum ???????????
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
            
            #l = []
            #l.extend(gestures[i].bins_left_filtered)
            #l.extend(gestures[i].bins_right_filtered)
            #l.extend(gestures[i].featureVector)
            #data.append(l)
            
            data.append(featureVector)
        return data
            