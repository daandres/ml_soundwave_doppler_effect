from classifier.classifier import IClassifier
from pybrain.structure import LSTMLayer, LinearLayer, SoftmaxLayer, SigmoidLayer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.validation import ModuleValidator, CrossValidator
import classifier.lstm.util as util
import numpy as np
from scipy import stats as stats
import time
# import arac
from systemkeys import SystemKeys

INPUTS = 24
NAME = "LSTM"

class LSTM(IClassifier):

    def __init__(self, recorder=None, config=None, relative=""):
        self.recorder = recorder
        self.config = config
        self.customName = self.config['customname']
        self.hidden = int(self.config['hiddenneurons'])
        self.peepholes = bool(self.config['peepholes'])
        self.epochs = int(self.config['trainingepochs'])
        self.trainedEpochs = 0
        self.classes = eval(self.config['classes'])
        self.nClasses = len(self.classes)
        self.trainingType = self.config['training']
        self.relative = relative
        self.avg = util.preprocessFrame(util.getAverage())
        self.trainer, self.returnsNet = None, False
        self.layer = self.config['outlayer']
        self.loadData(self.config['dataset'])
        if(self.config['autoload_network'] == "true"):
            self.load()
        else:
            self._createNetwork()

        self.datalist = []
        self.datanum = 0
        self.has32 = False
        self.previouspredict = 6
        self.predcounter = 0
        self.predHistSize = 8
        self.predHistHalfUpper = 5
        self.predHistory = util.createArraySix(self.predHistSize,)

        # Classify3 method
        self.predhistoryforclassify3 = []

        self.outkeys = SystemKeys()

#======================================================================
#=Interface methods====================================================
#======================================================================

    def getName(self):
        return NAME

    def startTraining(self, args=[]):
        def __getGradientTrainer():
            print("LSTM Gradient " + self.config['trainingalgo'] + " Training started")
            trainAlgo = util.getGradientTrainAlgo(self.config['trainingalgo'])
            trainer = trainAlgo(self.net, dataset=self.ds, verbose=True)
            return trainer, False

        def __getOptimizationTrainer():
            print("LSTM Optimization " + self.config['trainingalgo'] + " Training started")
            trainAlgo = util.getOptimizationTrainAlgo(self.config['trainingalgo'])
            l = trainAlgo(self.ds.evaluateModuleMSE, self.net, verbose=True)
            return l, True

        def __train(training, returnsNet):
            start = time.time()
            print("start training of " + str(self.epochs) + " epochs: " + str(start / 3600))
            print(self.__getName())
            if(self.epochs >= 10):
                tenthOfEpochs = self.epochs / 10
                for i in range(10):
                    inBetweenStart = time.time()
                    if returnsNet: self.net = training(tenthOfEpochs)
                    else: training(tenthOfEpochs)
                    end = time.time()
                    diff = end - inBetweenStart
                    print("Training time of epoch " + str(i) + " : " + str(end / 3600) + "\nDiff: " + str(diff / 3600))
                lastEpochs = self.epochs - (tenthOfEpochs * 10)
            else:
                lastEpochs = self.epochs
            if(lastEpochs > 0):
                if returnsNet: self.net = training(lastEpochs)
                else: training(lastEpochs)
            end = time.time()
            diff = end - start
            self.trainedEpochs += self.epochs
            print("Training end: " + str(end / 3600) + "\nDiff: " + str(diff / 3600))
            if(self.config['autosave_network'] == "true"):
                filename = self.__getName() + "_" + str(time.time())
                self.save(filename, overwrite=False)
            self.startValidation()
            return

        #==========
        # =Training=
        if(args != [] and len(args) >= 2):
            self.epochs = int(args[1])
        if(self.trainingType == "gradient"):
            if(self.trainer == None):
                self.trainer, self.returnsNet = __getGradientTrainer();
            __train(self.trainer.trainEpochs, self.returnsNet)
        elif(self.trainingType == "optimization"):
            if(self.trainer == None):
                self.trainer, self.returnsNet = __getOptimizationTrainer();
            __train(self.trainer.learn, self.returnsNet)
            return
        elif(self.trainingType == "crossval"):
            if(self.trainer == None):
                self.trainer, self.returnsNet = __getGradientTrainer();
            evaluation = ModuleValidator.classificationPerformance(self.trainer.module, self.ds)
            validator = CrossValidator(trainer=self.trainer, dataset=self.trainer.ds, n_folds=5, valfunc=evaluation, verbose=True, max_epochs=1)
            print(validator.validate())
        else:
            raise Exception("Cannot create trainer, no network type specified")

    def classify(self, data):
        normalizedData = data / np.amax(data)
        preprocessedData = util.preprocessFrame(normalizedData)
        diffAvgData = preprocessedData - self.avg
        self.__classify2(diffAvgData)


    def startValidation(self):
        print(self.testds.evaluateModuleMSE(self.net))
        self.__confmat()

    def load(self, filename=""):
        if filename == "":
            filename = self.config['network']
        self.net = util.load_network(self.config['networkpath'] + filename)
        self.net.sorted = False
        self.net.sortModules()
        netValues = util.parseNetworkFilename(filename)
        for key, value in netValues.items():
            if(key == 'neurons'):
                self.hidden = int(value)
            elif(key == 'epochs'):
                self.trainedEpochs = int(value)
            elif(key == 'layer'):
                self.layer = value
            elif(key == 'nClasses'):
                self.nClasses = int(value)
            elif(key == 'trainer'):
                self.trainingType = value
            elif(key == 'peepholes'):
                self.peepholes = bool(value)

    def save(self, filename="", overwrite=True):
        if filename == "":
            if overwrite:
                filename = self.config['network']
            else:
                filename = self.config['network'] + str(time.time())
        util.save_network(self.net, self.config['networkpath'] + filename)

    def loadData(self, filename=""):
        if(self.config['autoload_data'] == "true"):
            if filename == "":
                filename = self.config['dataset']
            self.ds = util.load_dataset(filename)
        else:
            self.ds = util.createPyBrainDatasetFromSamples(self.classes, self.nClasses, "", self.config['data_average'], self.config['merge67'])
        self.testds, self.ds = self.ds.splitWithProportion(0.2)

    def saveData(self, filename=""):
        if filename == "":
            filename = self.config['dataset']
        util.save_dataset(self.ds, filename)

    def printClassifier(self):
        print(self.__getName())
        util.printNetwork(self.net)

#======================================================================
#=Internal methods=====================================================
#======================================================================


    def _createNetwork(self):
        if(self.layer == "linear"): layer = LinearLayer
        elif(self.layer == "sigmoid"): layer = SigmoidLayer
        elif(self.layer == "softmax"): layer = SoftmaxLayer
        else: raise Exception("Cannot create network: no output layer specified")
        self.net = buildNetwork(INPUTS, self.hidden, self.nClasses, hiddenclass=LSTMLayer, outclass=layer, recurrent=True, outputbias=False, peepholes=self.peepholes)
        if(self.config['fast'] != ""):
            self.net = self.net.convertToFastNetwork()
        self.net.randomize()
        print("LSTM network created: " + self.__getName())
        return

    '''
    Activates a sequence and sums up the results for each activation and returns the highest value
    '''
    def _activateSequence(self, dataList):
        out = np.zeros(self.nClasses)
        for data in dataList:
            out += self.net.activate(data)
        return np.argmax(out)

    '''
    Calculates the confmat based on the testdataset and calculates the error
    
    Altenrative for error calculation, but without confmat:
    trnresult = 100. * (1.0 - testOnSequenceData(self.net, self.testds))
    '''

    def __confmat(self):
        confmat = np.zeros((self.nClasses, self.nClasses))
        for i in range(self.testds.getNumSequences()):
            self.net.reset()
            sequence = self.testds.getSequence(i)
            target = np.argmax(sequence[1][31])
            out = self._activateSequence(sequence[0])
            confmat[target][out] += 1
        sumWrong = 0
        sumAll = 0
        for i in range(self.nClasses):
            for j in range(self.nClasses):
                if i != j:
                    sumWrong += confmat[i][j]
                sumAll += confmat[i][j]
        error = sumWrong / sumAll
        np.set_printoptions(suppress=True)
        print(confmat)
        print("Validation error: %5.2f%%" % (100. * error))

    def __getName(self):
        return self.customName + "n" + str(self.hidden) + "_o" + str(self.nClasses) + "_l" + self.layer + "_p" + str(self.peepholes) + "_t" + self.trainingType + "_e" + str(self.trainedEpochs) + self.config['fast']

    '''
    Gesten werden starr nach 32 frames erkannt
    '''
    def __classify1(self, data):
        self.datalist.append(data)
        self.datanum += 1
        if(self.datanum % 32 == 0):
            self.net.reset()
            out = self._activateSequence(self.datalist)
            print(str(out))
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
        self.datanum += 1
        self.datalist.append(data)
        if(self.datanum % 32 == 0):
            self.has32 = True
        if(self.has32):
            self.net.reset()
            Y_pred = self._activateSequence(self.datalist)
            del self.datalist[0]
            self.predHistory[0] = Y_pred
            self.predHistory = np.roll(self.predHistory, -1)
            expected = stats.mode(self.predHistory, 0)
            if(expected[1][0] >= self.predHistHalfUpper):
                if(int(expected[0][0]) != self.previouspredict):
                    oldPrevious, oldPredCounter = self.previouspredict, self.previouspredict
                    self.previouspredict = int(expected[0][0])
                    self.predcounter = 1
                    return oldPrevious, oldPredCounter
                else:
                    self.predcounter += 1
                    if(self.predcounter == 4):
                        print self.previouspredict
                        self.outkeys.outForClass(self.previouspredict)
                    return self.previouspredict, self.predcounter
        return -1, -1


    '''
    Gesten werden innerhalb von der Geste 6 gesucht
    TODO not finished yet
    '''
    def __classify3(self, data):
        pred, predcounter = self.__classifiy2(data)
        if(pred != -1 and predcounter >= 4):
            try:
                prevpred, prevpredcounter = self.predhistoryforclassify3.pop()
                if(prevpred != pred):
                    self.predhistoryforclassify3.append([prevpred, prevpredcounter])
            except IndexError:
                pass
            self.predhistoryforclassify3.append([pred, predcounter])
            if(pred == 6 and len(self.predhistoryforclassify3) <= 1):
                pass
            else:
                classes = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
                for pred, count in self.predhistoryforclassify3:
                    classes[pred] += count
                classes.pop(6)
                classifiedclass = stats.mode(np.asarray(classes.values()), 0)
                print classifiedclass


    '''
    Gesten werden anhand eines erkannten Starttresholds erkannt
    '''
    def __classify4(self, data):
        # sequence maximum erkennen
        pass

