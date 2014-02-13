import numpy as np
import sys
from threading import Thread
import time

import classifier.hmm.config.config as c
import classifier.hmm.util.dataUtil as d
import classifier.hmm.util.hmmUtil as h
import ConfigParser
import pickle
from classifier.classifier import IClassifier
import classifier.hmm.plot as plot
import win32com.client
import os

NAME = "HiddenMarkovModel"
GESTURE_PREFIX="gesture "


class HMM(IClassifier):

    def __init__(self, recorder=None, config=None, relative=""):
        self.classList = c.classList
        self.du = d.DataUtil()
        self.gestureApp = GestureApplication(self.du)
        self.n_windows = c.n_windows
        self.gestureWindows=[[]]*self.n_windows
        self.activeWindow = 0
        self.framesCut = round((c.framesBefore+c.framesAfter+1))/2
        if os.name == 'nt':
            self.isWindows = True
            self.shell = win32com.client.Dispatch("WScript.Shell")
        else:
            self.isWindows = False

    def getName(self):
        return NAME

    def printClassifier(self):
        return NAME

    def startTraining(self, args=[]):
        return self.gestureApp.createGestures(self.classList)

    def classify(self, data):
        
        for i in range(self.n_windows):
            self.gestureWindows[i].append(data)
            gestureWindow = self.gestureWindows[i]
            # window is full
            if (len(gestureWindow)==c.framesTotal):
                seq = np.array([gestureWindow])
                self.startClassificationAction(seq)
                self.gestureWindows[i] = []
                
            if (len(gestureWindow)==(c.framesTotal-self.framesCut)) and (self.activeWindow == i):
                self.gestureWindows[(i+1)%self.n_windows] = []
                self.activeWindow = (i+1)%self.n_windows
        

    def startClassificationAction(self,seq):
        seq = self.du.preprocessData(seq)
        if len(seq) != 0:
            gesture, prob =  self.gestureApp.scoreSeqLive(seq[0])
            if gesture == None:
                return
            if (gesture.className != 'gesture 7'):
                print gesture, prob
            if self.isWindows:
                if (gesture.className == 'gesture 1'):
                    self.shell.SendKeys("{PGDN}",0)
                if (gesture.className == 'gesture 5'):
                    self.shell.SendKeys("{PGUP}",0)
                
                
    def startValidation(self):
        ret = []
        for className, dataPath in self.classList:
            obs, test = self.du.loadSplitData(dataPath)
            if np.shape(obs)[0] > 1:
                ret.append(GestureApplication.scoreClassData(test, className))
        return ret

    def load(self, filename=""):
        pass


    def save(self, filename=""):
        pass


    def loadData(self, filename=""):
        gesture = int(filename)
        p = plot.Plot(gesture, gmms=self._getGMMDic())
        p.initPlot()
        
    def _getGMMDic(self):
        dic = {}
        for gesture in self.gestureApp.gestures.values():
            gestureNum = gesture.getClassNum()
            hmm = gesture.getHMM()
            dic[gestureNum] = hmm.gmms_
        return dic

    def saveData(self, filename=""):
        self.gestureApp.trainAndSave()



class GestureApplication():
    
    def __init__(self, du=d.DataUtil()):
        self.du = du
        self.classList = c.classList
        self.gestures = {}
        
        if c.train:
            self.trainAndSave()
        else:
            try:
                self.loadModels('classifier/hmm/data/' + c.trainedModel + '.cfg')
            except Exception:
                ''' Create HMM Model based on all existing Gesture datasets '''
                self.gestures = {}
                self.trainAndSave()

    def createGesture(self, gesture, className):
        mu = h.HMM_Util()
        obs, test = self.du.loadSplitData(gesture)
        if np.shape(obs)[0] > 1:
            gesture = Gesture(className)
            print "### building " + str(className) + " ###"
            print " training " + str(len(obs)) + ", testing " + str(len(test)) 
            hmm, logprob = mu.buildModel(obs, test)
            gesture.setHMM(hmm)
        
            return gesture
        return None
        
    def createGestures(self, classList):
        ''' classList = [1, 2, 3] '''

        for g in classList:
            className = GESTURE_PREFIX + str(g)
            gesture = self.createGesture(g, className)
            if gesture != None:
                self.gestures[g] = gesture

    def scoreData(self, data):
        
        ''' find most likely class '''
        scoreList = []
        for seq in data:
            scoreList.append(self.scoreSeq(seq))
        return scoreList

    def scoreClassData(self, data, className):
        
        ''' find most likely class '''
        scores = {}
        probs = []
        for seq in data:
            gesture, prob = self.scoreSeq(seq)
            if gesture is not None:
                scores[gesture.className] = scores.get(gesture.className, 0) + 1
                probs.append(prob)
        accuracy = 100.0 * scores.get(className, 0) / len(data)*1.0
        return scores, round(accuracy, 2), className
            
    def scoreSeq(self, seq):
        
        ''' find most likely class '''
        logprob = -sys.maxint - 1
        gesture = None
        for g in self.gestures.values():
            if  (g.className == 'gesture 2') | (g.className == 'gesture 4'):
                continue
            l = g.score(seq)
            #print 'alle: '+str(l), g
            if 0 > l >= logprob:
                logprob = l
                gesture = g 
        return gesture, logprob
    
    def scoreSeqLive(self, seq):
        
        ''' find most likely class '''
        logprob1 = -sys.maxint - 1
        logprob2 = -sys.maxint - 1
        gesture = None
        for g in self.gestures.values():
            l = g.score(seq)
            #print ' '+str(l), g
            if 0 > l >= logprob1:
                logprob2 = logprob1
                logprob1 = l
                gesture = g 
        if (logprob1*c.classificationTreshhold + logprob1) < logprob2:
            return None, None
        return gesture, logprob1
    
    def saveModels(self, filePath, configurationName='Default'):
        config = ConfigParser.RawConfigParser()
        config.add_section('General')
        config.set('General','Configuration Name', configurationName)
        config.set('General','Number of gestures', len(self.gestures))
        for ges in self.gestures.values():
            config.add_section(ges.className)
            config.set(ges.className,'hmm',pickle.dumps(ges))
        with open(filePath, 'wb') as configfile:
            config.write(configfile)
    
    def loadModels(self, filePath):
        config = ConfigParser.ConfigParser()
        config.read(filePath)
        classList = config.get('General', 'configuration name').split(", ")
        for i in classList:
            configName = GESTURE_PREFIX+str(i)
            try:
                gestureConfig = str(config.get(configName,'hmm'))
                gesture = pickle.loads(gestureConfig)
                self.gestures[i] = (gesture)
            except Exception as e:
                print "problem :" + i

    def trainAndSave(self):
        print "hmm: start training"
        
        self.createGestures(self.classList)
        for classNum in self.classList:
            # score it
            className = GESTURE_PREFIX + str(classNum)
            obs, test = self.du.loadSplitData(classNum)
            if np.shape(obs)[0] > 1 :
                scores, accuracy, className = self.scoreClassData(test, className)
                print className, accuracy, scores
        
        timestamp = str(int(time.time()))
        self.saveModels('classifier/hmm/data/config_' + timestamp +'.cfg', str(c.classList).replace("[", "").replace("]", ""))
        print "hmm: training finished"



class Gesture():
    ''' Gesture Bean '''
    
    def __init__(self, className):
        self._hmm = None
        self.className = className
    
    def setHMM(self, hmm):
        self._hmm = hmm
    
    def getHMM(self):
        return self._hmm
    
    def getClassNum(self):
        return int(self.className.replace(GESTURE_PREFIX, ""))
    
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


    print "#### END ####"
