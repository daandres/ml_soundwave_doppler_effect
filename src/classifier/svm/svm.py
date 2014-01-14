'''
Created on 14/01/2014

@author: Benny
'''
from classifier.classifier import IClassifier

import numpy as np
import os
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score
from gestureFileIO import GestureFileIO

class SVM(IClassifier):
    
    def __init__(self, recorder=None, config=None, relative=""):
        self.avg = self.getAverage()
        self.classifier = self.load("classifier/svm/svm_trained.pkl")
        self.datalist = []
        self.datanum = 0
    
    def getAverage(self):
        g = GestureFileIO()
        avg = g.getAvgFrequency()
        return avg
    
    def load(self, filename=""):
        return joblib.load(filename)


    def classify(self, data):
        normalizedData = data / np.amax(data)
        diffAvgData = normalizedData - self.avg

        self.datanum += 1
        self.datalist.append(diffAvgData)
        if(self.datanum % 32 == 0):
            self.datanum = 0
            b = np.asarray(self.datalist).reshape(2048,)
            Y_pred = self.classifier.predict(b)
            self.datalist = []
            print Y_pred


    def getName(self):
        return "SVM"

    def startClassify(self):
        pass

    def startTraining(self):
        pass

    def startValidation(self):
        pass

    def save(self, filename=""):
        pass

    def loadData(self, filename=""):
        pass

    def saveData(self, filename=""):
        pass