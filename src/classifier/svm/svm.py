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
from collections import Counter
from scipy import stats as stats

class SVM(IClassifier):

    def __init__(self, recorder=None, config=None, relative=""):
        #self.avg = self.getAverage()
        self.classifier = self.load("classifier/svm/svm_trained.pkl")
        self.datalist = []
        self.datanum = 0
        self.nClasses = 7
        self.data, self.targets, self.avg = self.loadData()
        self.kernel = "rbf"
        self.c = 1000000
        self.gamma = 1
        self.degree = 3
        self.coef0 = 10

        self.has32 = False
        self.previouspredict = 6
        self.predcounter = 0
        self.predHistSize = 6
        self.predHistHalfUpper = 4
        self.predHistory = self.createArraySix(self.predHistSize,)
        
        self.foundgesture = False
        self.foundgestureindex = 0

    def createArraySix(self, dim):
        array = np.zeros((dim,))
        for i in range(dim):
            array[i] = 6
        return array

    def getAverage(self):
        g = GestureFileIO()
        avg = g.getAvgFrequency()
        return avg

    def load(self, filename=""):
        return joblib.load(filename)


    def classify(self, data):
        normalizedData = data / np.amax(data)
        diffAvgData = normalizedData - self.avg
        
        self.datalist.append(diffAvgData)
        self.datanum += 1
        
        #=======================================================================
        # T = diffAvgData - self.avg
        # diff = np.max(np.abs(T))
        # if diff < 1:
        #     self.foundgestureindex = self.datanum
        #=======================================================================

    
        plus = 8
        if(self.datanum == 32+plus):
            preds = []
            for i in range(plus):
                g = np.asarray(self.datalist[i:32+i]).reshape(2048,)
                Y_pred = self.classifier.predict(g)[0]
                preds.append(Y_pred)
            
            c = Counter(preds)
            
            #if np.unique(np.asarray(preds)).size != len(preds): # and (self.datanum-32-plus) < self.foundgestureindex:
            if max(set(preds), key=preds.count) != 6:
                #print preds
                print "unique classes:\t\t",len(list(set(preds)))
                print "count of classes:\t",c
                print "predicted class:\t",max(set(preds), key=preds.count)
                print "\n",60*"=","\n"
            self.datalist = []
            self.datanum = 0
            #print "\t\t\t new gesture"
            

    def classifyold(self, data):
        normalizedData = data / np.amax(data)
        diffAvgData = normalizedData - self.avg

        self.datanum += 1
        self.datalist.append(diffAvgData)
        if(self.datanum % 32 == 0):
            self.has32 = True
        if(self.has32):
            b = np.asarray(self.datalist[0:32]).reshape(2048,)
            Y_pred = self.classifier.predict(b)[0]
            self.predHistory[0] = Y_pred
            self.predHistory = np.roll(self.predHistory, -1)
            expected = stats.mode(self.predHistory, 0)
            if(expected[1][0] >= self.predHistHalfUpper):
#             if(not (np.shape(expected[0])[0] >= 2)):
                if(int(expected[0][0]) != self.previouspredict):
                    self.previouspredict = int(expected[0][0])
                    print self.previouspredict
#                 self.datanum = 0
#                 self.datalist = []
#                 self.has32 = False
#             else:
            del self.datalist[0]


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
        
        def normalise(arr, nn_avg):
            ''' normalise each frame '''
            for d in range(len(arr)):
                for dd in range(len(arr[d])):
                    arr[d][dd] = (arr[d][dd] / np.amax(arr[d][dd])) - nn_avg
            return arr
        
        names = ["Benjamin"]
        path = "../gestures/"

        ''' load and reshape textfile with 18.5khz frequency data '''
        n = np.loadtxt(path + "Benjamin/gesture_6/1390243484.txt", delimiter=",")
        n = n.reshape(n.shape[0], 32, n.shape[1] / 32)  # recordingframes
        nn = normalise(n, 0)
        nn_avg = np.mean(nn, axis=1)
        nn_avg = np.mean(nn_avg, axis=0)

    
        gestures = []
        targets = []
        for gesturenumber in range(7):
            for name in names:
                dirf = os.listdir(path + name + "/gesture_" + str(gesturenumber))

                for txtfile in dirf:
                    ''' load and reshape textfile with gesture data '''
                    g = np.loadtxt(path + name + "/gesture_" + str(gesturenumber) + "/" + txtfile, delimiter=",")
                    g = g.reshape(g.shape[0], 32, g.shape[1] / 32)  # recordingframes
                    print name, gesturenumber, "\t\t", g.shape, txtfile
                    gn = normalise(g, nn_avg)
    
                    gn = gn.reshape(gn.shape[0], gn.shape[1] * gn.shape[2])
    
                    for i in range(gn.shape[0]):
                        gestures.append(gn[i])
                        targets.append(gesturenumber)
    
        data = np.array(gestures)
        targets = np.array(targets)
        
        print data.shape, targets.shape
        
        return data, targets, nn_avg

    def loadData_old(self, filename=""):
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
