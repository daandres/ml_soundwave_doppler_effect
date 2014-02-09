#!/usr/bin/env python
# -*- coding: utf-8 -*-
import classifier.trees.ProcessData
'''
This class reads raw training data from local files and provide data and targets
'''
class TrainingData(object):

    def __init__(self, gesture_ids):
        self.gestures = []
        self.targets = []
        for gesture_id in gesture_ids:
            filename = "../gestures/Annalena/gesture_%d/data.txt" % gesture_id
            print "loading dataset", filename
            data = classifier.trees.ProcessData.getTestData(filename)
            self.gestures += data
            
            for i in range(len(data)):
                self.targets.append(gesture_id)
            
       
    def getRawData(self):
        return self.gestures
    
    def getTargets(self):
        return self.targets
        