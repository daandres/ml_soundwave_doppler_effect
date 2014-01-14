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
        self.nClasses = 7
        self.loadData()

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
        confmat = np.zeros((self.nClasses, self.nClasses))
#         print("target-out")
        for c in range(self.data.shape[0]):
            out = None
            target = c
            j = 0
            for geste in self.data[c]:
                out = self.classifier.predict(geste)
                confmat[target][out[0]] += 1
#             print("out:\t" + str(out) + "\ttarget:\t" + str(target))
#             print(str(np.argmax(target)) + "-" + str(np.argmax(out)))
        sumWrong = 0
        sumAll = 0
        for i in range(self.nClasses):
            for j in range(self.nClasses):
                if i != j:
                    sumWrong += confmat[i][j]
                sumAll += confmat[i][j]
        error = sumWrong / sumAll
        print(confmat)
        print("error: " + str(100. * error) + "%")

    def save(self, filename=""):
        pass

    def loadData(self, filename=""):
        g = GestureFileIO()
        data = [0] * self.nClasses
        for i in range(self.nClasses):
            datum = g.getGesture3DDiffAvg(i, [])
            print("data " + str(i) + " loaded shape: " + str(np.shape(datum)))
            data[i] = datum.reshape(datum.shape[0], datum.shape[1] * datum.shape[2])
        data = np.asarray(data)
        self.data = data


    def saveData(self, filename=""):
        pass
