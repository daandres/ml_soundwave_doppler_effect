import classifier.lstm.util as util
import numpy as np
from scipy import stats as stats
import properties.config as c
import operator

'''
LSTMCLassify class provides different methods for live/online classification with the LSTM Module. 
It also calls the Systemkeys class to bind keys to classes and execute the bindings
'''
class LSTMClassify():

    def __init__(self, config, net):
        self.config = config
        self.net = net
        self.avg = util.getAverage(self.net.datacut, self.net.datafold)

        self.datalist = []
        self.datanum = 0
        self.has32 = False

        # Classify2
        self.previouspredict = 6
        self.predcounter = 0
        self.predHistSize = 8
        self.predHistHalfUpper = 5
        self.predcountertreshold = 5
        self.predHistory = util.createArraySix(self.predHistSize,)

        # Classify3 method
        self.predhistoryforclassify3 = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
        self.classify3start = False

        # classify4
        self.start = 0
        self.buffer = []
        self.liveData = []
        self.beginClassify = 0
        self.beginMax = 0
        self.maxValue = 0
        self.maxValueList = []

        # For interacting with OS
        self.outkeys = None
        if(c.getInstance().getOSConfig()['type'] == "posix"):
            from systemkeys import SystemKeys
            self.outkeys = SystemKeys()

    '''
    Interface method for classifcation. WIll be called by LSTM interface and calls different implementations. 
    Preprocess data. 
    '''
    def classify(self, data):
        preprocessedData = data / np.amax(data)
        preprocessedData = util.preprocessFrame(preprocessedData, self.net.datacut, self.net.datafold)
        # diffAvgData = preprocessedData - self.avg
        out = self.__classify3(preprocessedData)
        if(out != -1):
            print("Gesture " + str(out) + " detected")
            if(self.outkeys != None):
                self.outkeys.outForClass(out)

    '''
    Gesten werden starr nach 32 frames erkannt
    '''
    def __classify1(self, data):
        data = data - self.avg
        self.datalist.append(data)
        self.datanum += 1
        if(self.datanum % 32 == 0):
            self.net.reset()
            out = self.net._activateSequence(self.datalist)
            self.datalist = []
            self.datanum = 0
            return out
        return -1

    '''
    Gesten werden auf folgende Art erkannt:
    - wenn 32 Datensaetze vorhanden sind wird das Netz aktiviert und der Output in eine Liste gespeichert
    - Diese Liste wird staendig erweitert und hat ein feste Laenge (siehe self.predHistory in init)
    - Es wird der Modus der Liste gebildet
    - Ist der Modus ueber einem  bestimmten Treshold (self.predHistHalfUpper) wird der Wert in self.previouspredict gespeichert
    - Ist previouspredict 4 mal gleich wird die Gestenklasse ausgegeben, ist die Klasse groesser als 4 mal gleich erfolgt keine neue Ausgabe
    - 
    '''
    def __classify2(self, data):
        data = data - self.avg
        self.datanum += 1
        self.datalist.append(data)
        if(self.datanum % 32 == 0):
            self.has32 = True
        if(self.has32):
            # Activate for 32 Frames
            self.net.reset()
            Y_pred = self.net._activateSequence(self.datalist)
            del self.datalist[0]

            # Save network output in list
            self.predHistory[0] = Y_pred
            self.predHistory = np.roll(self.predHistory, -1)

            # Get Mode of list
            expected = stats.mode(self.predHistory, 0)

            # Check if Mode count is greater than self.predHistHalfUpper
            if(expected[1][0] >= self.predHistHalfUpper):
                # If current mode is not the most one, change it and reset counter
                if(int(expected[0][0]) != self.previouspredict):
                    self.previouspredict = int(expected[0][0])
                    self.predcounter = 1
                # else increase counter and return class if counter is greater then
                else:
                    self.predcounter += 1
                    if((self.predcounter == self.predcountertreshold)):
                        return self.previouspredict
        return -1


    '''
    Gesten werden innerhalb von der Geste 6 gesucht
    '''
    def __classify3(self, data):
        pred = self.__classify2(data)
        if(pred == 6):
            # check for most classified class
            if(not self.classify3start):
                self.classify3start = True
                return -1
            print self.predhistoryforclassify3
            highestkey = 6
            highestkey = max(self.predhistoryforclassify3.iteritems(), key=operator.itemgetter(1))[0]
            self.predhistoryforclassify3 = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
            return highestkey

        if(self.classify3start):
            if(pred != -1 and self.predcounter >= 4):
                self.predhistoryforclassify3[pred] += self.predcounter

        return -1

    '''
    Gesten werden anhand eines erkannten Starttresholds erkannt
    '''
    def __classify4(self, data):
        if not self.beginClassify:
            # collecting live data for avg
            self.liveData.append(data)
            if self.liveData.__len__() == 20:
                self.beginClassify = 1
                # print self.liveData
                self.avg = np.mean(self.liveData, axis=0)
                # print self.avg
                self.beginMax = 1
        # collecting data for maxValue
        elif self.beginMax:
            data = data - self.avg
            self.maxValueList.append(data.max())
            if self.maxValueList.__len__() == 30:
                for a in self.maxValueList:
                    if self.maxValue < a:
                        self.maxValue = a
                print self.maxValue
                # maxValue ein bischen erhohen (steuert empfindlichkeit der erkennung)
                self.maxValue = self.maxValue + 0.0001
                self.beginMax = 0
        else:
            data = data - self.avg
            # print data.max()
            if data.max() > self.maxValue and self.start == 0:
                print "starting ..."
                self.start = 1

            if self.start:
                self.datalist.append(data)
                self.datanum += 1
                if(self.datanum % 32 == 0):
                    print "net ac"
                    self.net.reset()
                    out = self.net._activateSequence(self.datalist)
                    print(str(out))
                    self.datalist = []
                    self.datanum = 0
                    self.start = 0
                    return out

        return -1

    '''
    Gesten werden anhand eines erkannten Starttresholds erkannt
    '''
    def __classify5(self, data):
        if not self.beginClassify:
            # collecting live data for avg
            self.liveData.append(data)
            if self.liveData.__len__() == 20:
                self.beginClassify = 1
                # print self.liveData
                self.avg = np.mean(self.liveData, axis=0)
                # print self.avg
                self.beginMax = 1
        # collecting data for maxValue
        elif self.beginMax:
            data = data - self.avg
            self.maxValueList.append(data.max())
            if self.maxValueList.__len__() == 30:
                for a in self.maxValueList:
                    if self.maxValue < a:
                        self.maxValue = a
                print self.maxValue
                # maxValue ein bischen erhohen (steuert empfindlichkeit der erkennung)
                self.maxValue = self.maxValue + 0.05
                self.beginMax = 0
        else:
            data = data - self.avg
            # print data.max()
            if self.buffer.__len__() <= 10 and not self.start:
                self.buffer.append(data)
            elif self.buffer.__len__() == 11 and not self.start:
                self.buffer.pop(0)
                self.buffer.append(data)
            if data.max() > self.maxValue and self.start == 0:
                print "starting ..."
                self.start = 1

            if self.start:
                self.datalist.append(data)
                if(self.datalist.__len__() + self.buffer.__len__()) % 32 == 0:
                    print "net ac"
                    print "buffer: " + str(self.buffer.__len__())
                    print "list: " + str(self.datalist.__len__())
                    self.net.reset()
                    out = self.net._activateSequence(self.datalist)
                    print(str(out))
                    self.datalist = []
                    self.buffer = []
                    self.datanum = 0
                    self.start = 0
                    return out

        return -1
