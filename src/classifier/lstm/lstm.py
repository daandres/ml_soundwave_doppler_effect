from classifier.classifier import IClassifier
from pybrain.structure import LSTMLayer, LinearLayer, SoftmaxLayer, SigmoidLayer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.validation import testOnSequenceData
import classifier.lstm.util as util
import numpy as np
from scipy import stats as stats
import time
import arac

INPUTS = 64
NAME = "LSTM"

class LSTM(IClassifier):

    def __init__(self, recorder=None, config=None, relative=""):
        self.recorder = recorder
        self.config = config
        self.hidden = int(self.config['hiddenneurons'])
        self.outneurons = int(self.config['outneurons'])
        self.epochs = int(self.config['trainingepochs'])
        self.trainedEpochs = 0
        self.classes = eval(self.config['classes'])
        self.nClasses = len(self.classes)
        self.trainingType = self.config['training']
        self.relative = relative
        self.avg = util.getAverage()
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
            print("start training of " + str(self.epochs) + " epochs: " + str(start / 3600)) + self.__getName()
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
        else:
            raise Exception("Cannot create trainer, no network type specified")

    def classify(self, data):
        normalizedData = data / np.amax(data)
        diffAvgData = normalizedData - self.avg

        self.__classifiy2(diffAvgData)


    def startValidation(self):
        trnresult = 100. * (1.0 - testOnSequenceData(self.net, self.ds))
        print("Validation error: %5.2f%%" % trnresult)
        print(self.ds.evaluateModuleMSE(self.net))
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
            elif(key == 'nclasses'):
                self.nClasses = int(value)
            elif(key == 'epochs'):
                self.trainedEpochs = int(value)
            elif(key == 'layer'):
                self.layer = value
            elif(key == 'outneurons'):
                self.outneurons = int(value)
            elif(key == 'trainer'):
                self.trainingType = value

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
            self.ds = util.createPyBrainDatasetFromSamples(self.classes, INPUTS, self.outneurons, "", self.config['data_average'], self.config['merge67'])

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
        self.net = buildNetwork(INPUTS, self.hidden, self.outneurons, hiddenclass=LSTMLayer, outclass=layer, recurrent=True, outputbias=False)
        if(self.config['fast'] != ""):
            self.net = self.net.convertToFastNetwork()
        self.net.randomize()
        print("LSTM network created: " + self.__getName())
        return

    def __confmat(self):
        confmat = np.zeros((self.nClasses, self.nClasses))
        for i in range(self.ds.getNumSequences()):
            self.net.reset()
            out = None
            target = None
            j = 0
            for dataIter in self.ds.getSequenceIterator(i):
                data = dataIter[0]
                target = dataIter[1]
                out = self.net.activate(data)
                j += 1
            confmat[np.argmax(target)][np.argmax(out)] += 1
        sumWrong = 0
        sumAll = 0
        for i in range(self.outneurons):
            for j in range(self.outneurons):
                if i != j:
                    sumWrong += confmat[i][j]
                sumAll += confmat[i][j]
        error = sumWrong / sumAll
        print(confmat)
        print("error: " + str(100. * error) + "%")

    def __getName(self):
        return "n" + str(self.hidden) + "_o" + str(self.outneurons) + "_l" + self.layer + "_nC" + str(self.nClasses) + "_t" + self.trainingType + "_e" + str(self.trainedEpochs) + self.config['fast']


    def __classify1(self, data):
        out = self.net.activate(data)
        self.datanum += 1
        if(self.datanum % 32 == 0):
            self.datanum = 0
            self.net.reset()
            print(str(np.argmax(out)) + " " + str(out))

    def __classifiy2(self, data):
        self.datanum += 1
        self.datalist.append(data)
        if(self.datanum % 32 == 0):
            self.has32 = True
        if(self.has32):
            self.net.reset()
            for i in range(32):
                out = self.net.activate(self.datalist[i])
            Y_pred = np.argmax(out)
            self.predHistory[0] = Y_pred
            self.predHistory = np.roll(self.predHistory, -1)
            expected = stats.mode(self.predHistory, 0)
            if(expected[1][0] >= self.predHistHalfUpper):
#             if(not (np.shape(expected[0])[0] >= 2)):
                if(int(expected[0][0]) != self.previouspredict):
                    self.previouspredict = int(expected[0][0])
                    self.predcounter = 1
#                 self.datanum = 0
#                 self.datalist = []
#                 self.has32 = False
                else:
                    self.predcounter += 1
                    if(self.predcounter == 4):
                        print self.previouspredict
            del self.datalist[0]
