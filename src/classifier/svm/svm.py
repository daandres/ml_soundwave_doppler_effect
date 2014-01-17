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
from sklearn import svm
from sklearn import cross_validation


class SVM(IClassifier):

    def __init__(self, recorder=None, config=None, relative=""):
        self.avg = self.getAverage()
        self.classifier = self.load("classifier/svm/svm_trained.pkl")
        self.datalist = []
        self.datanum = 0
        self.nClasses = 7
        self.data, self.targets = self.loadData()
        self.kernel = "rbf"
        self.c = 1000000
        self.gamma = 1
        self.degree = 3
        self.coef0 = 10

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
        temp = 8
        has32 = False
        if(self.datanum % 32 == 0):
            has32 = True
        previouspredict = 6
        predcounter = 0
        if(has32):
#             predictedlist = np.zeros((self.nClasses,))
#             for i in range(temp):
            b = np.asarray(self.datalist[0:32]).reshape(2048,)
            Y_pred = self.classifier.predict(b)[0]
            if(previouspredict == Y_pred):
                print "equal ", Y_pred
                predcounter += 1
                if(predcounter >= 3):
                    print Y_pred
#                     break
            else:
                print "not equal ", Y_pred
                previouspredict = Y_pred
                predcounter = 1
            self.datalist.pop(0)
            print len(self.datalist)
#                 predictedlist[Y_pred] += 1
#             print predictedlist, np.argmax(predictedlist, 0)
#             self.datalist = []
#             self.datanum = 0


    def getName(self):
        return "SVM"

    def startClassify(self):
        pass

    def startTraining(self, args=[]):
        classifier = svm.SVC(kernel=self.kernel, C=self.c, gamma=self.gamma, degree=self.degree, coef0=self.coef0)
        classifier.fit(self.data, self.targets)
        joblib.dump(classifier, 'classifier/svm/svm_trained.pkl', compress=9)

    def startValidation(self):
        confmat = np.zeros((self.nClasses, self.nClasses))
        for i in range(len(self.targets)):
            realclass = self.targets[i]
            predictedclass = self.classifier.predict(self.data[i])[0]
            confmat[realclass][predictedclass] += 1

        #=======================================================================
        # for c in range(self.data.shape[0]):
        #     out = None
        #     target = c
        #     j = 0
        #     for geste in self.data[c]:
        #         out = self.classifier.predict(geste)
        #         confmat[target][out[0]] += 1
        #=======================================================================
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
        X = []
        Y = []
        for i in range(self.nClasses):
            datum = g.getGesture3DDiffAvg(i, [], True)
            if(i == 6):
                data7 = g.getGesture3DDiffAvg(7, [], True)
                datum = np.append(datum, data7, axis=0)
            print("data " + str(i) + " loaded shape: " + str(np.shape(datum)))
            d = datum.reshape(datum.shape[0], datum.shape[1] * datum.shape[2])
            for dd in range(d.shape[0]):
                X.append(d[dd])
                Y.append(i)

        data = np.asarray(X)
        targets = np.asarray(Y)
        print data.shape, targets.shape
        return data, targets


    def saveData(self, filename=""):
        pass

    def printClassifier(self):
        return
