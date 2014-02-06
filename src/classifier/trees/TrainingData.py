#!/usr/bin/env python
# -*- coding: utf-8 -*-
import classifier.trees.ProcessData

class TrainingData(object):

    def __init__(self):
        self.gestures = classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_2/1391437451.txt")
        self.gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_2/1391437809.txt")
        self.gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_3/1391439011.txt")
        self.gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_3/1391439281.txt")
        self.gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_4/1391439536.txt")
        self.gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_4/1391439659.txt")
        #gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_0/1391435081.txt")
        #gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_0/1391435669.txt")
        self.gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_1/1391436572.txt")
        self.gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_1/1391436738.txt")
        self.gestures += classifier.trees.ProcessData.getTestData("../gestures/Daniel/gesture_6/gesture_6_zimmer_1.txt")
        self.gestures += classifier.trees.ProcessData.getTestData("../gestures/Daniel/gesture_6/gesture_6_zimmer_3.txt")
       
        self.targets = []
       
        for class_ in [2,2,3,3,4,4,1,1,6,6]:
            for frameIndex in range(50):
                self.targets.append(class_)
       
    def getRawData(self):
        return self.gestures
    
    def getTargets(self):
        return self.targets
        