'''
Created on 14/01/2014

@author: Benny, Manuel
'''

import os
import numpy as np
import subprocess as sp
import pylab as pl
import warnings

from sklearn.externals import joblib
from sklearn import svm
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

from gestureFileIO import GestureFileIO
from classifier.classifier import IClassifier
#import properties.config as config

''' catch warnings as error '''
np.set_printoptions(precision=4, suppress=True, threshold='nan')
np.seterr(all='warn')
warnings.simplefilter("error", RuntimeWarning)

''' Usage:
> t
> l classifier/svm/svm_trained.pkl
> c 
'''


class SVM(IClassifier):
    SLICE_LEFT = 12
    SLICE_RIGHT = 12
    NUM_SAMPLES_PER_FRAME = 64  #config.leftBorder + config.rightBorder

    def __init__(self, recorder=None, config=None, relative=""):
        self.gestures_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'gestures')
        self.path = os.path.join(os.path.dirname(__file__), 'svm_trained.pkl')
        self.classifier = self.load(self.path)
        self.subdirs = ["Benjamin","Alex"]#,"Alex","Daniel"]
        
        self.datalist = []
        self.datanum = 0
        self.num_gestures = 7
        self.nClasses = 7
        self.new = True
        self.framerange = 20
        self.timeout = 10
        self.threshold = 0.1
        #self.data, self.targets, self.avg = self.loadData() #, self.avg
        self.noise_frame = self.load_noise_frame()
        self.X_train, self.X_test, self.Y_train, self.Y_test = self.loadData()
        #self.data, self.targets = self.loadData()
        
        # SVM parameters
        self.kernel = "rbf"
        self.c = 1.0
        self.gamma = 0.1
        self.degree = 3
        self.coef0 = 0.0
        
        #=======================================================================
        # for c in range(1,1000,100):
        #     self.c = c
        #     for gamma in range(10):
        #         self.gamma = gamma
        #         print c, gamma
        #         self.startTraining(None)
        #         self.startValidation()
        #=======================================================================
        


        self.predicted = False
        self.gesturefound = False
        self.gestureindex = 0
        self.executed = {"notepad": False, "taskmgr": False, "calc": False}

    @staticmethod
    def normalise_framesets(framesets, noise_frame):
        ''' normalise framesets and substract noiseframe '''
        for frameset_nr in range(len(framesets)):
            for frame_nr in range(len(framesets[frameset_nr])):
                current_frameset = framesets[frameset_nr][frame_nr]
                framesets[frameset_nr][frame_nr] = (current_frameset / np.amax(current_frameset)) - noise_frame
        return framesets
    
    def preprocess_frame(self, dataframe, noise):
        try:
            ''' normalise and slice dataframe '''
            normalized_data_with_noise = dataframe / np.amax(dataframe)
            normalized_data = normalized_data_with_noise - noise
            
            ''' set small noisy data to 0 '''
            frame = normalized_data
            irrelevant_samples = np.where(frame <= self.threshold)
            frame[irrelevant_samples] = 0.0
        except:
            frame = np.zeros(dataframe.shape[0])

        return frame
    
    @staticmethod
    def slice_frame(frame):
        return frame[SVM.SLICE_LEFT:(SVM.NUM_SAMPLES_PER_FRAME - SVM.SLICE_RIGHT)]
    
    @staticmethod
    def slice_framesets(framesets):
        return framesets[:, :, SVM.SLICE_LEFT:(SVM.NUM_SAMPLES_PER_FRAME - SVM.SLICE_RIGHT)]

    @staticmethod
    def load_gesture_framesets(txt_file):
        gesture_plain = np.loadtxt(txt_file, delimiter=",")  # all frames in one array
        num_framesets = gesture_plain.shape[0]
        num_samples_total = gesture_plain.shape[1]
        num_frames_per_frameset = num_samples_total / SVM.NUM_SAMPLES_PER_FRAME

        gesture_framesets_plain = gesture_plain.reshape(num_framesets, num_frames_per_frameset,
                                                        SVM.NUM_SAMPLES_PER_FRAME)  # split the array to a frameset
        return gesture_framesets_plain

    def load_noise_frame(self):
        noise_txt_file = os.path.join(self.gestures_path, 'Benjamin', 'gesture_6', '1389637026.txt')

        ''' load and reshape textfile with 18.5khz no gesture frequency data '''
        noise_framesets_plain = self.load_gesture_framesets(noise_txt_file)
        noise_framesets = self.normalise_framesets(noise_framesets_plain, 0) # max amplitude = 1, dont subtract noise
        noise_avg_frameset = np.mean(noise_framesets, axis=1) # reduce to 1 frame per frameset
        noise_frame = self.slice_frame(np.mean(noise_avg_frameset, axis=0))
        return noise_frame

    def loadData(self, filename=""):
        

        gestures = []
        targets = []
        for gesture_nr in range(self.num_gestures):
            print "load gesture", gesture_nr
            for subdir in self.subdirs:
                #dirf = os.listdir(os.path.join(self.gestures_path, subdir, 'gesture_' + str(gesture_nr)))
                files = [c for a,b,c in os.walk(os.path.join(self.gestures_path, subdir, 'gesture_' + str(gesture_nr)))][0]
                for textfile in files:
                    ''' load and reshape textfile with gesture data '''
                    gesture_framesets_plain = self.load_gesture_framesets(os.path.join(self.gestures_path, subdir, 'gesture_' + str(gesture_nr), textfile))
                    gesture_framesets = self.slice_framesets(gesture_framesets_plain)
                    
                    ''' create one gesture frame from relevant frames '''
                    for frameset_nr in range(gesture_framesets.shape[0]):

                        if self.new:
                            current_frameset = [self.preprocess_frame(frame, self.noise_frame) for frame in gesture_framesets[frameset_nr] if np.amax(self.preprocess_frame(frame, self.noise_frame)) > 0]
                            while len(current_frameset) < 16:
                                current_frameset.append(np.zeros(40))
                            
                            even = current_frameset[:16:2] 
                            odd = current_frameset[1:16:2]
                            test = np.asarray(list(np.asarray(even) + np.asarray(odd)))
                            normalised_gesture_frame = test.reshape(40*8,)
                            
                        else:
                            current_frameset = [self.preprocess_frame(frame, self.noise_frame) for frame in gesture_framesets[frameset_nr]]
                            gesture_frame = np.asarray(current_frameset).sum(axis=0)
    
                            ''' normalise summed gesture frame '''
                            try:
                                normalised_gesture_frame = gesture_frame / np.amax(gesture_frame)
                            except RuntimeWarning:
                                normalised_gesture_frame = np.zeros(gesture_frame.shape[0])
                        
                        gestures.append(normalised_gesture_frame)
                        targets.append(gesture_nr)

        data = np.array(gestures)
        targets = np.array(targets)
        print data.shape, targets.shape
        
        return train_test_split(data, targets, random_state=0)
    
        return data, targets
    

    def classify(self, data):
        ''' start preprocessing of framedata '''
        frame = self.preprocess_frame(self.slice_frame(data),self.noise_frame)
        
        ''' store frame in datalist and increment running index '''
        self.datalist.append(frame)
        self.datanum += 1
        
        if self.timeout < self.framerange/2:
            self.timeout += 1
            if self.timeout == self.framerange/2:
                print "..."
        
        ''' check if frame has some relevant information and store this running index '''
        if np.amax(frame) > 0.0 and self.gesturefound == False and self.timeout == self.framerange/2:
            self.gestureindex = self.datanum
            self.gesturefound = True
            
        ''' check if framerange is reached and gesturefound is true '''
        if self.gestureindex + self.framerange == self.datanum and self.gesturefound == True:
            self.gestureindex = 0
            self.gesturefound = False
            self.timeout = 0
            
            
            if self.new:
                current_frameset = [frame for frame in self.datalist[-self.framerange:] if np.amax(frame) > 0]
                while len(current_frameset) < 16:
                    current_frameset.append(np.zeros(40))
                
                even = current_frameset[:16:2] 
                odd = current_frameset[1:16:2]
                test = np.asarray(list(np.asarray(even) + np.asarray(odd)))
                normalised_gesture_frame = test.reshape(40*8,)

                target_prediction = self.classifier.predict(normalised_gesture_frame)[0]  # only each second?!?
                self.executeCommand(target_prediction)
                
            else:
                ''' add all frames to one gestureframe '''
                current_frameset = np.asarray(self.datalist[-self.framerange:])
                gesture_frame = current_frameset.sum(axis=0)
                
                try:
                    ''' normalise gestureframe '''
                    normalised_gesture_frame = gesture_frame / np.amax(gesture_frame)
                    if not np.isnan(np.sum(normalised_gesture_frame)):
                        
                        ''' start actual classification '''
                        target_prediction = self.classifier.predict(normalised_gesture_frame)[0]  # only each second?!?
                        self.executeCommand(target_prediction)
                except:
                    print "error =("

        ''' delete unneeded frames from datalist '''
        if self.datanum > self.framerange:
            del self.datalist[0]


    def load(self, filename=""):
        try:
            return joblib.load(filename)
        except:
            print "file does not exist"


    def executeCommand(self, number):
        if number != 6:

            if number == 0 and self.executed["notepad"] == False:
                print "\t",str(number),"=>","starting notepad"
                proc = sp.Popen("notepad")
                self.executed["notepad"] = proc.pid
    
            elif number == 1 and self.executed["notepad"] != False:
                print "\t",str(number),"=>","terminating notepad"
                sp.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.executed["notepad"]), shell=True, stdout=sp.PIPE)
                self.executed["notepad"] = False
    
            elif number == 2 and self.executed["taskmgr"] == False:
                print "\t",str(number),"=>","starting taskmanager"
                proc = sp.Popen("taskmgr")
                self.executed["taskmgr"] = proc.pid
    
            elif number == 3 and self.executed["taskmgr"] != False:
                print "\t",str(number),"=>","terminating taskmanager"
                sp.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.executed["taskmgr"]), shell=True, stdout=sp.PIPE)
                self.executed["taskmgr"] = False
    
            elif number == 4 and self.executed["calc"] == False:
                print "\t",str(number),"=>","starting calculator"
                proc = sp.Popen("calc")
                self.executed["calc"] = proc.pid
    
            elif number == 5 and self.executed["calc"] != False:
                print "\t",str(number),"=>","terminating calculator"
                sp.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.executed["calc"]), shell=True, stdout=sp.PIPE)
                self.executed["calc"] = False
    
            
            elif number == 1 and self.executed["notepad"] == False:
                print "\t",str(number),"=>","notepad not started, nothing to terminate"
            elif number == 3 and self.executed["taskmgr"] == False:
                print "\t",str(number),"=>","taskmanager not started, nothing to terminate"
            elif number == 5 and self.executed["calc"] == False:
                print "\t",str(number),"=>","calculator not started, nothing to terminate"
                
            elif number == 0 and self.executed["notepad"] != False:
                print "\t",str(number),"=>","notepad already started, only one instance allowed"
            elif number == 2 and self.executed["taskmgr"] != False:
                print "\t",str(number),"=>","taskmanager already started, only one instance allowed"
            elif number == 4 and self.executed["calc"] != False:
                print "\t",str(number),"=>","calculator already started, only one instance allowed"


    
    def getName(self):
        return "SVM"


    def startTraining(self, args=[]):
        classifier = svm.SVC(kernel=self.kernel, C=self.c, gamma=self.gamma, degree=self.degree, coef0=self.coef0)
        #classifier.fit(self.data, self.targets)
        classifier.fit(self.X_train, self.Y_train)

        joblib.dump(classifier, self.path, compress=9)
        self.classifier = classifier


    def startValidation(self):
        l = len(self.Y_train) / 10
        p = 0
        confmat = np.zeros((self.nClasses, self.nClasses))
        for i in range(len(self.Y_train)):
            if (i + 1) % l == 0:
                p += 10
                print p, "%"
            realclass = self.Y_train[i]
            predictedclass = self.classifier.predict(self.X_train[i])[0]
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

    def loadData__(self, filename=""):
        g = GestureFileIO()
        X = []
        Y = []
        for i in range(self.nClasses):
            datum = g.getGesture3DDiffAvg(i, [], True)
            if (i == 6):
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
        XT = XX[:, :,
             [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
              40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53]]
        for gi in range(len(XT)):
            temp = []
            for rf in range(len(XT[gi])):
                frame = XT[gi][rf] ** 2
                cond = np.where(frame <= 0.025)
                frame[cond] = 0
                if np.amax(frame) > 0:
                    temp.append(frame)

            allg = np.asarray(temp)

            muh = np.zeros(40)
            for t in allg:
                muh += t

            try:
                kuh = muh / np.amax(muh)
            except RuntimeWarning:
                kuh = np.zeros(40)

            gestures.append(kuh[::2])

        data = np.asarray(gestures)

        print data.shape, targets.shape

        if False:
            shuffle = np.random.permutation(np.arange(data.shape[0]))
            data, targets = data[shuffle], targets[shuffle]

            split = len(data) / 4

            X_train = data[:split * 3]
            Y_train = targets[:split * 3]
            X_test = data[split * 3:]
            Y_test = targets[split * 3:]

            print X_train.shape, Y_train.shape, X_test.shape, Y_test.shape

            settings = {}
            smallesterror = 100
            for e in range(3, 10):
                for f in range(5):
                    kernel = "sigmoid"
                    c = 10.0 ** e
                    g = f
                    degree = e
                    coef0 = f
                    print("training kernel with (c:" + str(c) + ", gamma:" + str(g) + ", degree:" + str(
                        degree) + ", coef0:" + str(coef0) )
                    clf = svm.SVC(kernel=kernel, C=c, gamma=g, degree=degree, coef0=coef0)
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
        print self.path
        
    def show_confusion_matrix(self):
        # Compute confusion matrix
        target_names = ["gesture 0","gesture 1","gesture 2","gesture 3","gesture 4","gesture 5","gesture 6"]
        self.Y_pred = self.classifier.predict(self.X_test)
        cm = confusion_matrix(self.Y_test, self.Y_pred)
        print(cm)
        print(classification_report(self.Y_test, self.Y_pred, target_names=target_names))
        definition = '''
        The precision is the ratio tp / (tp + fp) where tp is the number of true positives and fp the number of false positives.
        The precision is intuitively the ability of the classifier not to label as positive a sample that is negative.

        The recall is the ratio tp / (tp + fn) where tp is the number of true positives and fn the number of false negatives.
        The recall is intuitively the ability of the classifier to find all the positive samples.
        
        The F-beta score can be interpreted as a weighted harmonic mean of the precision and recall, 
        where an F-beta score reaches its best value at 1 and worst score at 0.
        
        The F-beta score weights recall more than precision by a factor of beta.
        beta == 1.0 means recall and precision are equally important.
        
        The support is the number of occurrences of each class in y_true.
        '''
        print definition
        # Show confusion matrix in a separate window
        pl.matshow(cm)
        pl.title('Confusion matrix')
        pl.colorbar()
        pl.ylabel('Actual gestures')
        pl.xlabel('Predicted gestures')
        pl.show()
