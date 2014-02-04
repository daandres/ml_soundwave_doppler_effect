import numpy as np
import sys
from threading import Thread
import time

import config.config as c
import util.dataUtil as d
import util.hmmUtil as h
import util.util as u

from classifier.classifier import IClassifier
from src.gestureFileIO import GestureFileIO


NAME = "HiddenMarkovModel"
GESTURE_PREFIX="gesture "

class HMM(IClassifier):

    def __init__(self, recorder=None, config=None, relative=""):
        self.recorder = recorder
        self.config = config
        self.relative = relative
        self.gestureApp = GestureApplication()
        self.classList = [("gesture 0", "data/gesture_0.txt"), ("gesture 3", "data/gesture_3.txt"), ("gesture 5", "data/gesture_5.txt"), ("clean", "data/clean.txt")]
        self.fileIO = GestureFileIO()

    def getName(self):
        return NAME

    def printClassifier(self):
        return NAME

    def startTraining(self, args=[]):
        return self.gestureApp.createGestures(self.classList)


    def classify(self, data):
        dim = len(np.shape(data))
        #several obs
        if dim == 3:
            return self.gestureApp.scoreData(data)
        # only one obs
        elif dim == 2:
            return self.gestureApp.scoreSeq(data) 


    def startValidation(self):
        ret = []
        for className, dataPath in classList:
            obs, test = u.loadSplitData(dataPath)
            ret.append(GestureApplication.scoreClassData(test, className))
        return ret

    def load(self, filename=""):
        pass


    def save(self, filename=""):
        pass


    def loadData(self, filename=""):
        pass


    def saveData(self, filename=""):
        pass



class GestureApplication():
    
    def __init__(self):
        self.dp = d.DataUtil()
        self.mu = h.HMM_Util()
        self.gestures = []
        self.fileIO = GestureFileIO()
               
    def createGesture(self, gesture, className):
        obs, test = u.loadSplitData(gesture)
            
        gesture = Gesture(className)
        print "### building " + str(className) + " ###"
        print " training " + str(len(obs)) + ", testing " + str(len(test)) 
        hmm, logprob = self.mu.buildModel(obs, test)
        gesture.setHMM(hmm)
        self.gestures.append(gesture)
        
    def createGestures(self, classList):
        ''' classList = [1, 2, 3] '''
        for gesture in classList:
            className = GESTURE_PREFIX + str(gesture)
            self.createGesture(gesture, className)

    def scoreData(self, data):
        
        ''' find most likely class '''
        scoreList = []
        for seq in data:
            scoreList.append(self.scoreSeq(seq))
        return scoreList

    def scoreClassData(self, data, className):
        
        ''' find most likely class '''
        scores = {}
        for seq in data:
            gesture, _ = self.scoreSeq(seq)
            if gesture is not None:
                scores[gesture.className] = scores.get(gesture.className, 0) + 1
        accuracy = 100.0 * scores.get(className, 0) / len(data)*1.0
        return scores, round(accuracy, 2), className
            
    def scoreSeq(self, seq):
        
        ''' find most likely class '''
        logprob = -sys.maxint - 1
        gesture = None
        for g in self.gestures:
            l = g.score(seq)
            
            if 0 > l > logprob:
                logprob = l
                gesture = g 
        return gesture, logprob
    
    def saveModels(self):
        ''' TODO '''
        return
    
    def loadModels(self):
        ''' TODO '''
        return


class Gesture():
    ''' Gesture Bean '''
    
    def __init__(self, className):
        self._hmm = None
        self.className = className
    
    def setHMM(self, hmm):
        self._hmm = hmm
    
    def getHMM(self):
        return self._hmm
    
    def score(self, seq):
        return self._hmm.score(seq)
    
    def scoreList(self, obs):
        ''' returns average score, single score list of observations, '''
        scoreList = []
        for seq in obs:
            scoreList.append(self.score(seq))
        return np.average(scoreList), scoreList

    def __repr__(self):
        return self.className
    
    __str__ = __repr__


if __name__ == "__main__":
    print "#### START ####"

    classList = [0, 1, 3, 5, 7]
    ga = GestureApplication()
    ga.createGestures(classList)

    for classNum in classList:
        className = GESTURE_PREFIX + str(classNum)
        obs, test = u.loadSplitData(classNum)
        print ga.scoreClassData(obs, className)
        print ga.scoreClassData(test, className)
    

    print "#### END ####"