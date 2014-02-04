'''
Created on 14/01/2014

@author: Benny
'''
from classifier.classifier import IClassifier

import numpy as np
import os
from sklearn.externals import joblib
from gestureFileIO import GestureFileIO
from sklearn import svm
from scipy import stats as stats
import subprocess as sp


np.set_printoptions(precision=4,suppress=True,threshold='nan')
np.seterr(all='warn')
import warnings
warnings.simplefilter("error", RuntimeWarning)


class SVM(IClassifier):

    def __init__(self, recorder=None, config=None, relative=""):
        #self.avg = self.getAverage()[:,[14, 15,16,17,18,19, 20,21,22,23,24, 25,26,27,28,29, 30,31,32,33,34, 35,36,37,38,39, 40,41,42,43,44, 45,46,47,48,49, 50,51,52,53]]
        self.classifier = self.load("classifier/svm/svm_trained.pkl")
        self.datalist = []
        self.datanum = 0
        self.nClasses = 7
        self.data, self.targets, self.avg  = self.loadData() #, self.avg 
        self.kernel = "poly"
        self.c = 1
        self.gamma = 1
        self.degree = 3
        self.coef0 = 1
        
        self.predicted = False
        self.predHistory = []
        
        self.found = False
        self.index = 0
        
        self.executed = {"notepad": False, "taskmgr": False, "calc": False}

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
        try:
            return joblib.load(filename)
        except:
            print "file does not exist"



    def classify(self,data):
        normalizedData = data / np.amax(data)
        diffAvgData = normalizedData[14:54] - self.avg
        
        frame = diffAvgData**2
        cond = np.where(frame <= 0.025)
        frame[cond] = 0.0
        
        rr = 20
        self.datalist.append(frame)
        self.datanum += 1
        

        if np.amax(frame) > 0.0 and self.found == False:
            self.index = self.datanum
            self.found = True
        
        if self.index + rr == self.datanum and self.found == True: 
            self.index = 0
            self.found = False
            
            g = np.asarray(self.datalist[-rr:])
            temp = []
            for rf in range(len(g)):
                if np.amax(g[rf]) > 0.0:
                    temp.append(g[rf])
            
            allg = np.asarray(temp,dtype=np.float64)
            muh = np.zeros(40)
            for t in allg:
                muh += t

            try:
                kuh = muh/np.amax(muh)
                if not np.isnan(np.sum(kuh)):
                    Y_pred = self.classifier.predict(kuh[::2])[0]
                    if Y_pred != 6:
                        self.executeCommand(Y_pred)
            except:
                print "error =("
        
        if self.datanum > 40:
            del self.datalist[0]

            
    def executeCommand(self, number):
        print number, 
        
        if number == 0 and self.executed["notepad"] == False:
            print "starting notepad"
            proc = sp.Popen("notepad")
            self.executed["notepad"] = proc.pid

        elif number == 1 and self.executed["notepad"] != False:
            sp.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.executed["notepad"]))
            print "terminating notepad"
            self.executed["notepad"] = False
            
        elif number == 2 and self.executed["taskmgr"] == False:
            print "starting taskmanager"
            proc = sp.Popen("taskmgr")
            self.executed["taskmgr"] = proc.pid
            
        elif number == 3 and self.executed["taskmgr"] != False:
            sp.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.executed["taskmgr"]))
            print "terminating taskmanager"
            self.executed["taskmgr"] = False
        
        elif number == 4 and self.executed["calc"] == False:
            print "starting calculator"
            proc = sp.Popen("calc")
            self.executed["calc"] = proc.pid
        
        elif number == 5 and self.executed["calc"] != False:
            sp.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.executed["calc"]))
            print "terminating calculator"
            self.executed["calc"] = False
        
        print ""
        

    def classify3(self, data):
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
        l = len(self.targets)/10
        p = 0
        confmat = np.zeros((self.nClasses, self.nClasses))
        for i in range(len(self.targets)):
            if (i+1) % l == 0:
                p += 10
                print p, "%" 
            realclass = self.targets[i]
            predictedclass = self.classifier.predict(self.data[i])[0]
            confmat[realclass][predictedclass] += 1

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
        n = np.loadtxt(path + "Benjamin/gesture_6/1389637026.txt", delimiter=",")
        n = n.reshape(n.shape[0], 32, n.shape[1] / 32)  # recordingframes
        nn = normalise(n, 0)
        nn_avg = np.mean(nn, axis=1)
        nn_avg = np.mean(nn_avg, axis=0)
        avg = nn_avg[:,[14, 15,16,17,18,19, 20,21,22,23,24, 25,26,27,28,29, 30,31,32,33,34, 35,36,37,38,39, 40,41,42,43,44, 45,46,47,48,49, 50,51,52,53]]

    
        gestures = []
        targets = []
        for gesturenumber in range(7):
            print "Gesture", gesturenumber
            for name in names:
                dirf = os.listdir(path + name + "/gesture_" + str(gesturenumber))

                for txtfile in dirf:
                    ''' load and reshape textfile with gesture data '''
                    g = np.loadtxt(path + name + "/gesture_" + str(gesturenumber) + "/" + txtfile, delimiter=",")
                    g = g.reshape(g.shape[0], 32, g.shape[1] / 32)  # recordingframes
                    g_test = g[:,:,[14, 15,16,17,18,19, 20,21,22,23,24, 25,26,27,28,29, 30,31,32,33,34, 35,36,37,38,39, 40,41,42,43,44, 45,46,47,48,49, 50,51,52,53]]
                    gn = normalise(g_test, avg)

                    for i in range(gn.shape[0]):
                        #print "\tDataset", i, len(gn[i]), "\t\t", 
                        #print gn[i].shape
                        temp = []
                        for rf in range(len(gn[i])):
                            frame = gn[i][rf]**2
                            cond = np.where(frame <= 0.025)
                            frame[cond] = 0
                            if np.amax(frame) > 0:
                                temp.append(frame)
                        
                        #print ""
                        allg = np.asarray(temp)

                        muh = np.zeros(40)
                        for t in allg:
                            muh += t
                        try:
                            kuh = muh/np.amax(muh)
                        except RuntimeWarning:
                            kuh = np.zeros(40)
                            
                        gestures.append(kuh[::2])
                        targets.append(gesturenumber)
    
        data = np.array(gestures)
        targets = np.array(targets)

        print data.shape, targets.shape
        
        return data, targets, avg


    def loadData__(self, filename=""):
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

        XX = np.asarray(X)
        targets = np.asarray(Y)
        
        gestures = []
        XX = XX.reshape(XX.shape[0], 32, 64)
        XT = XX[:,:,[14, 15,16,17,18,19, 20,21,22,23,24, 25,26,27,28,29, 30,31,32,33,34, 35,36,37,38,39, 40,41,42,43,44, 45,46,47,48,49, 50,51,52,53]]
        for gi in range(len(XT)):
            temp = []
            for rf in range(len(XT[gi])):
                frame = XT[gi][rf]**2
                cond = np.where(frame <= 0.025)
                frame[cond] = 0
                if np.amax(frame) > 0:
                    temp.append(frame)

            allg = np.asarray(temp)

            muh = np.zeros(40)
            for t in allg:
                muh += t
                
            try:
                kuh = muh/np.amax(muh)
            except RuntimeWarning:
                kuh = np.zeros(40)
                
            gestures.append(kuh[::2])
        
        data = np.asarray(gestures)
        
        print data.shape, targets.shape
        
        if False:
            shuffle = np.random.permutation(np.arange(data.shape[0]))
            data, targets = data[shuffle], targets[shuffle]
            
            split = len(data)/4
            
            X_train = data[:split*3]
            Y_train = targets[:split*3]
            X_test = data[split*3:]
            Y_test = targets[split*3:]
            
            print X_train.shape, Y_train.shape, X_test.shape, Y_test.shape
            
            settings = {}
            smallesterror = 100
            for e in range(3,10):
                for f in range(5):
                    kernel = "sigmoid"
                    c = 10.0**e
                    g = f
                    degree = e
                    coef0 = f
                    print("training kernel with (c:" + str(c) + ", gamma:" + str(g) + ", degree:" + str(degree) + ", coef0:" + str(coef0) )
                    clf = svm.SVC(kernel=kernel,C=c,gamma=g,degree=degree,coef0=coef0)
                    clf.fit(X_train, Y_train)
                    
                    confmat = np.zeros((self.nClasses, self.nClasses))
                    for i in range(len(Y_test)):
                        realclass = Y_test[i]
                        predictedclass = clf.predict(X_test[i])[0]
                        confmat[realclass][predictedclass] += 1
            
                    sumWrong = 0
                    sumAll = 0
                    for i in range(self.nClasses):
                        for j in range(self.nClasses):
                            if i != j:
                                sumWrong += confmat[i][j]
                            sumAll += confmat[i][j]
                    error = (sumWrong / sumAll) * 100.
                    print(confmat)
                    print("error: " + str(error) + "%")
                    if error < smallesterror:
                        settings["c"] = c
                        settings["gamma"] = g
                        settings["degree"] = degree
                        settings["coef0"] = coef0
                        smallesterror = error
                        print "new settings", settings
                    print "\n"
            print settings
                
        return data, targets


    def saveData(self, filename=""):
        pass

    def printClassifier(self):
        return
