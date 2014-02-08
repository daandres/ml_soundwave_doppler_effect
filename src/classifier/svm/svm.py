'''
Created on 14/01/2014

@author: Benny, Manuel
'''


''' general imports '''
import os
import numpy as np
import pylab as pl
import warnings

''' explicit imports '''
from scipy.ndimage.filters import gaussian_filter1d
from sklearn.externals import joblib
from sklearn import svm
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

''' custom imports '''
from gestureFileIO import GestureFileIO
from classifier.classifier import IClassifier
from svm_dataloader import Dataloader
from svm_preprocessor import Preprocessor
from svm_appstarter import Starter

''' catch warnings as error '''
np.set_printoptions(precision=4, suppress=True, threshold='nan')
np.seterr(all='warn')
warnings.simplefilter("error", RuntimeWarning)


''' Usage '''
#===============================================================================
# > t
# > l classifier/svm/svm_trained.pkl
# > c 
#===============================================================================


class SVM(IClassifier):

    def __init__(self, recorder=None, config=None, relative=""):
        self.config = config
        self.appstarter = Starter()
        self.dataloader = Dataloader()
        self.preprocessor = Preprocessor()
                
        ''' general settings '''
        self.subdirs = self.config['used_gestures'].split(',')
        self.nClasses = int(self.config['used_classes'])
        
        ''' preprocessing settings '''
        self.slice_left = int(self.config['slice_left'])
        self.slice_right = int(self.config['slice_right'])
        self.samples_per_frame = int(self.config['samples_per_frame'])
        self.wanted_frames = self.samples_per_frame - self.slice_left - self.slice_right
        self.framerange = int(self.config['framerange'])
        self.timeout = int(self.config['timeout'])
        self.smooth = int(self.config['smooth'])
        self.use_each_second = int(self.config['use_each_second'])
        self.threshold = float(self.config['threshold'])
        self.new_preprocess = self.config['new_preprocess']
        
        ''' svm settings '''
        self.kernel = self.config['kernel']
        self.c = float(self.config['c'])
        self.gamma = float(self.config['gamma'])
        self.degree = int(self.config['degree'])
        self.coef0 = float(self.config['coef0'])
        
        ''' static settings ''' 
        self.gestures_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'gestures')
        self.path = os.path.join(os.path.dirname(__file__), 'svm_trained.pkl')
        
        self.datalist = []
        self.datanum = 0
        self.gesturefound = 0
        self.gestureindex = 0
        self.executed = {"notepad": False, "taskmgr": False, "calc": False}
        
        ''' initial methods '''
        self.classifier = self.load(self.path)
        self.ref_frequency_frame = self.load_ref_frequency_frame()
        #self.X_train, self.X_test, self.Y_train, self.Y_test = self.loadData()
        self.X_train, self.Y_train = None, None #self.loadData()
        self.X_test, self.Y_test = self.X_train, self.Y_train
        

    @staticmethod
    def normalise_framesets(framesets, ref_frequency_frame):
        ''' normalise framesets and substract ref_frequencyframe '''
        for frameset_nr in range(len(framesets)):
            for frame_nr in range(len(framesets[frameset_nr])):
                current_frameset = framesets[frameset_nr][frame_nr]
                framesets[frameset_nr][frame_nr] = (current_frameset / np.amax(current_frameset)) - ref_frequency_frame
        return framesets
    
    
    def preprocess_frame(self, dataframe, ref_frequency):
        try:
            ''' normalise and slice dataframe '''
            normalized_data_with_ref_frequency = dataframe / np.amax(dataframe)
            normalized_data = normalized_data_with_ref_frequency - ref_frequency
            
            ''' set small noisy data to 0 '''
            frame = normalized_data
            irrelevant_samples = np.where(frame <= self.threshold)
            frame[irrelevant_samples] = 0.0
        except:
            frame = np.zeros(self.wanted_frames)

        return frame
    
    
    def slice_frame(self, frame):
        ''' slice one single 1d-frame from 64 to 40 datavalues '''
        return frame[self.slice_left:(self.samples_per_frame - self.slice_right)]
    
    
    def slice_framesets(self, framesets):
        ''' slice 3d-framesets from 64 to 40 datavalues '''
        return framesets[:, :, self.slice_left:(self.samples_per_frame - self.slice_right)]

    
    def load_gesture_framesets(self, txt_file):
        ''' load gesture training datasets ''' 
        gesture_plain = np.loadtxt(txt_file, delimiter=",")
        num_framesets = gesture_plain.shape[0]
        num_samples_total = gesture_plain.shape[1]
        num_frames_per_frameset = num_samples_total / self.samples_per_frame
        gesture_framesets_plain = gesture_plain.reshape(num_framesets, num_frames_per_frameset, self.samples_per_frame)
        
        return gesture_framesets_plain

    
    def load_ref_frequency_frame(self):
        ref_frequency_txt_file = os.path.join(self.gestures_path, 'Benjamin', 'gesture_6', '1389637026.txt')

        ''' load and reshape referencefrequency data with 18500Hz '''
        ref_frequency_framesets_plain = self.load_gesture_framesets(ref_frequency_txt_file)
        ref_frequency_framesets = self.normalise_framesets(ref_frequency_framesets_plain, 0)
        
        ''' reduce to one single average referencefrequency frame and slice to 40 datavalues '''
        ref_frequency_avg_frameset = np.mean(ref_frequency_framesets, axis=1)
        ref_frequency_frame = self.slice_frame(np.mean(ref_frequency_avg_frameset, axis=0))
        
        return ref_frequency_frame


    def loadData(self, filename=""):
        gestures = []
        targets = []
        for gesture_nr in range(0,self.nClasses):
            print "load gesture", gesture_nr
            for subdir in self.subdirs:
                files = [allfiles for path,subdirs,allfiles in os.walk(os.path.join(self.gestures_path, subdir, 'gesture_' + str(gesture_nr)))][0]
                for textfile in files:
                    ''' load and reshape textfile with gesture data '''
                    gesture_framesets_plain = self.load_gesture_framesets(os.path.join(self.gestures_path, subdir, 'gesture_' + str(gesture_nr), textfile))
                    gesture_framesets = self.slice_framesets(gesture_framesets_plain)
                    
                    ''' create one gesture frame from relevant frames '''
                    for frameset_nr in range(0,gesture_framesets.shape[0]):
                        
                        # new second preprocess step
                        if self.new_preprocess:
                            ''' get first 16 recordingframes which contain relevant gesture information '''
                            ''' if less than 16, append frames with zeros '''
                            current_frameset = [self.preprocess_frame(frame, self.ref_frequency_frame) for frame in gesture_framesets[frameset_nr] if np.amax(self.preprocess_frame(frame, self.ref_frequency_frame)) > 0]
                            while len(current_frameset) < self.framerange/2:
                                current_frameset.append(np.zeros(self.wanted_frames))
                            current_frameset = np.asarray(current_frameset[:self.framerange/2])

                            ''' slice to two lists (even/odd) and sum every pair; reshape to 1d array '''
                            relevant_frames = np.asarray(list(current_frameset[:self.framerange/2:2] + current_frameset[1:self.framerange/2:2]))
                            if self.smooth:
                                if self.use_each_second:
                                    normalised_gesture_frame = gaussian_filter1d(relevant_frames.reshape(self.wanted_frames*self.framerange/4,), 1.5)[::2]
                                else:
                                    normalised_gesture_frame = gaussian_filter1d(relevant_frames.reshape(self.wanted_frames*self.framerange/4,), 1.5)
                            else:
                                normalised_gesture_frame = relevant_frames.reshape(self.wanted_frames*self.framerange/4,)
                            #===================================================
                            # ax = pl.subplot(1,1,0)
                            # ax.set_xlim([0,8*40])
                            # ax.set_ylim([-0.1,1.1])
                            # scaling = np.arange(8*40)
                            # pl.plot(scaling, normalised_gesture_frame, "g")
                            # pl.show()
                            # return
                            #===================================================
                            
                        
                        # old second preprocess step
                        else:
                            ''' sum up all wanted frames to one gestureframe '''
                            current_frameset = [self.preprocess_frame(frame, self.ref_frequency_frame) for frame in gesture_framesets[frameset_nr]]
                            gesture_frame = np.asarray(current_frameset).sum(axis=0)
    
                            ''' normalise summed gesture frame '''
                            try:
                                normalised_gesture_frame = gesture_frame / np.amax(gesture_frame)
                            except RuntimeWarning:
                                normalised_gesture_frame = np.zeros(gesture_frame.shape[0])
                        
                        ''' append gestureframe and targetclass to their corresponding arrays '''
                        gestures.append(normalised_gesture_frame)
                        targets.append(gesture_nr)
        
        ''' convert to numpy array '''
        data = np.array(gestures)
        targets = np.array(targets)
        print data.shape, targets.shape
        
        #return train_test_split(data, targets, random_state=0)
    
        return data, targets
    

    def classify(self, data):
        ''' start first preprocessing of framedata '''
        frame = self.preprocess_frame(self.slice_frame(data),self.ref_frequency_frame)
        
        ''' store frame in datalist and increment running index '''
        self.datalist.append(frame)
        self.datanum += 1
        
        ''' increment timeout value to allow user to move his hand without any classification after one gesture '''
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
            
            # new second preprocess step
            if self.new_preprocess:
                ''' get first 16 recordingframes which contain relevant gesture information '''
                ''' if less than 16, append frames with zeros '''
                current_frameset = [frame for frame in self.datalist[-self.framerange:] if np.amax(frame) > 0]
                while len(current_frameset) < self.framerange/2:
                    current_frameset.append(np.zeros(self.wanted_frames))

                ''' slice to two lists (even/odd) and sum every pair; reshape to 1d array '''
                relevant_frames = np.asarray(list(np.asarray(current_frameset[:self.framerange/2:2] ) + np.asarray(current_frameset[1:self.framerange/2:2])))
                if self.smooth:
                    if self.use_each_second:
                        normalised_gesture_frame = gaussian_filter1d(relevant_frames.reshape(self.wanted_frames*self.framerange/4,), 1.5)[::2]
                    else:
                        normalised_gesture_frame = gaussian_filter1d(relevant_frames.reshape(self.wanted_frames*self.framerange/4,), 1.5)
                else:
                    normalised_gesture_frame = relevant_frames.reshape(self.wanted_frames*self.framerange/4,)
                
                try:
                    ''' start actual classification and applicationstarter '''
                    target_prediction = self.classifier.predict(normalised_gesture_frame)[0]  # only each second?!?
                    self.appstarter.controlProgram(target_prediction)
                except:
                    print "some error occured =("
                
            # old second preprocess step
            else:
                ''' sum up all wanted frames to one gestureframe '''
                current_frameset = np.asarray(self.datalist[-self.framerange:])
                gesture_frame = current_frameset.sum(axis=0)
                
                try:
                    ''' normalise gestureframe '''
                    normalised_gesture_frame = gesture_frame / np.amax(gesture_frame)
                    if not np.isnan(np.sum(normalised_gesture_frame)):
                        
                        ''' start actual classification and applicationstarter '''
                        target_prediction = self.classifier.predict(normalised_gesture_frame)[0]  # only each second?!?
                        self.starter.controlProgram(target_prediction)
                except:
                    print "some error occured =("

        ''' delete unneeded frames from datalist '''
        if self.datanum > self.framerange:
            del self.datalist[0]


    def load(self, filename=""):
        try:
            return joblib.load(filename)
        except:
            print "file does not exist"


    def getName(self):
        return "SVM"


    def startTraining(self, args=[]):
        self.X_train, self.Y_train = self.loadData()
        
        ''' start training '''
        classifier = svm.SVC(kernel=self.kernel, C=self.c, gamma=self.gamma, degree=self.degree, coef0=self.coef0)
        classifier.fit(self.X_train, self.Y_train)

        ''' save classifier and store reference in global variable '''
        joblib.dump(classifier, self.path, compress=9)
        self.classifier = classifier


    def startValidation(self):
        ''' own implementation of confusion matrix '''
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
        
        ''' compute error '''
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


    def saveData(self, filename=""):
        pass


    def printClassifier(self):
        print self.path
        print self.classifier
        
        
    def show_confusion_matrix(self):
        ''' method for creating confusion matrix with graphical visualization '''
        ''' callable from separate svm_conf.py module '''
        
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
        
        ''' plot confusion matrix in a separate window '''
        pl.matshow(cm)
        pl.title('Confusion matrix')
        pl.colorbar()
        pl.ylabel('Actual gestures')
        pl.xlabel('Predicted gestures')
        pl.show()
