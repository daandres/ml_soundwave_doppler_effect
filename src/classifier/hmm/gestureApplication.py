import numpy as np
import sys
from threading import Thread
import time

import classifier.hmm.config.config as c
import classifier.hmm.util.dataUtil as d
import classifier.hmm.util.hmmUtil as h
import classifier.hmm.util.util as u
import ConfigParser
import pickle
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
        self.gestureWindow1=[]
        self.gestureWindow2=[]
        self.isFirstRun = True

    def getName(self):
        return NAME

    def printClassifier(self):
        return NAME

    def startTraining(self, args=[]):
        return self.gestureApp.createGestures(self.classList)


    def classify(self, data):
        if(len(self.gestureWindow1)==32):
            seq = np.array([self.gestureWindow1])
            self.gestureApp.scoreSeq(seq)
            self.gestureWindow1[:] = []
        if self.isFirstRun:
            if(len(self.gestureWindow1)==16):
                self.gestureWindow2[:] = []
                self.isFirstRun = False
        if (len(self.gestureWindow2)==32):
                seq = np.array([self.gestureWindow2])
                self.gestureApp.scoreSeq(seq)
                self.gestureWindow2[:] = []
        self.gestureWindow1.append(data)
        self.gestureWindow2.append(data)


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
        self.loadModels('classifier/hmm/data/config.cfg')
        print 'tataa'
        '''
        classList = [0, 3]
        self.createGestures(classList)
        for classNum in classList:
            className = GESTURE_PREFIX + str(classNum)
            obs, test = u.loadSplitData(classNum)
            print self.scoreClassData(obs, className)
            print self.scoreClassData(test, className)
        self.saveModels('classifier/hmm/data/config.cfg')
        '''
               
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
        data = self.dp.reduceBins(seq)
        data = self.dp.normalize(data)
        data = self.dp.normalizeBound(data)
        data = self.dp.cutRelevantAction(data)
        data = self.dp.round(data)
        data = self.dp.cutBad(data)

        gesture = None
        for g in self.gestures:
            l = g.score(data[0])
            
            if 0 > l > logprob:
                logprob = l
                gesture = g 
        print gesture, logprob
    
    def saveModels(self, filePath, configurationName='Default'):
        config = ConfigParser.RawConfigParser()
        config.add_section('General')
        config.set('General','Configuration Name', configurationName)
        config.set('General','Number of gestures', len(self.gestures))
        i = 0
        for ges in self.gestures:
            config.add_section('Gesture'+str(i))
            config.set('Gesture'+str(i),'hmm',pickle.dumps(ges))
            i += 1
        with open(filePath, 'wb') as configfile:
            config.write(configfile)
    
    def loadModels(self, filePath):
        config = ConfigParser.ConfigParser()
        config.read(filePath)
        numberOfGestures = config.getint('General', 'number of gestures')
        for i in range(numberOfGestures):
            gestureConfig = str(config.get('Gesture'+str(i),'hmm'))
            #print gestureConfig
            hmm = pickle.loads(gestureConfig)
            self.gestures.append(hmm)


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