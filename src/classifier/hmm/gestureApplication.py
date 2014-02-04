import numpy as np
import sys

import config.config as c
import util.dataUtil as d
import util.hmmUtil as h
import util.util as u

class GestureApplication():
    
    def __init__(self):
        self.dp = d.DataUtil()
        self.mu = h.HMM_Util()
        self.gestures = []
               
    def createGesture(self, className, dataPath):
        gesture = Gesture(className)
        obs, test = u.loadSplitData(dataPath)
        hmm, logprob = self.mu.buildModel(obs, test)
        gesture.setHMM(hmm)
        self.gestures.append(gesture)
        
    def createGestures(self, classList):
        ''' classList = [(className, dataPath), (className, dataPath)] '''
        for className, dataPath in classList:
            self.createGesture(className, dataPath)

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

    classList = [("gesture 0", "data/gesture_0.txt"), ("gesture 3", "data/gesture_3.txt"), ("gesture 5", "data/gesture_5.txt"), ("clean", "data/clean.txt")]
    ga = GestureApplication()
    ga.createGestures(classList)

    for className, dataPath in classList:
        obs, test = u.loadSplitData(dataPath)
        print ga.scoreClassData(obs, className)
    

    print "#### END ####"