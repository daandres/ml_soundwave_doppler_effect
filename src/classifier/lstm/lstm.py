from classifier.classifier import IClassifier
from pybrain.structure import LSTMLayer, LinearLayer, SoftmaxLayer, SigmoidLayer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.validation import testOnSequenceData
import classifier.lstm.util as util
import numpy as np
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
        self.classes = eval(self.config['classes'])
        self.nClasses = len(self.classes)
        self.trainingType = self.config['training']
        self.datanum = 0
        self.relative = relative
        self.name = "n" + str(self.hidden) + "_o" + str(self.outneurons) + "_l" + self.config['outlayer'] + "_nC" + str(self.nClasses) + "_t" + self.trainingType + "_e" + str(self.epochs) + self.config['fast']
        self.avg = util.getAverage()
        self.loadData(self.config['dataset'])
        if(self.config['autoload_network'] == "true"):
            self.load()
        else:
            self._createNetwork()

#======================================================================
#=Interface methods====================================================
#======================================================================

    def getName(self):
        return NAME

    def startTraining(self):
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
            print("start training: " + str(start / 3600)) + self.name
            tenthOfEpochs = self.epochs / 10
            for i in range(10):
                inBetweenStart = time.time()
                if returnsNet: self.net = training(tenthOfEpochs)
                else: training(tenthOfEpochs)
                end = time.time()
                diff = end - inBetweenStart
                print("Training time of epoch " + str(i) + " : " + str(end / 3600) + "\nDiff: " + str(diff / 3600))
            lastEpochs = self.epochs - (tenthOfEpochs * 10)
            if(lastEpochs > 0):
                if returnsNet: self.net = training(lastEpochs)
                else: training(lastEpochs)
            end = time.time()
            diff = end - start
            print("Training end: " + str(end / 3600) + "\nDiff: " + str(diff / 3600))
            if(self.config['autosave_network'] == "true"):
                filename = self.name + "_" + str(time.time())
                self.save(filename, overwrite=False)
            self.startValidation()
            return

        #==========
        # =Training=
        if(self.trainingType == "gradient"):
            trainer, returnsNet = __getGradientTrainer();
            __train(trainer.trainEpochs, returnsNet)
        elif(self.trainingType == "optimization"):
            trainer, returnsNet = __getOptimizationTrainer();
            __train(trainer.learn, returnsNet)
            return
        else:
            raise Exception("Cannot create trainer, no network type specified")


    def classify(self, data):
        normalizedData = data / np.amax(data)
        diffAvgData = normalizedData - self.avg
        out = self.net.activate(diffAvgData)
        self.datanum += 1
        if(self.datanum % 32 == 0):
            self.datanum = 0
            self.net.reset()
            print(str(np.argmax(out)) + " " + str(out))

    def startValidation(self):
        trnresult = 100. * (1.0 - testOnSequenceData(self.net, self.ds))
        print("Validation error: %5.2f%%" % trnresult)
        print(self.ds.evaluateModuleMSE(self.net))
        self.__confmat()

    def load(self, filename=""):
        if filename == "":
            filename = self.config['network']
        self.net = util.load_network(filename)
        self.net.sorted = False
        self.net.sortModules()

    def save(self, filename="", overwrite=True):
        if filename == "":
            if overwrite:
                filename = self.config['network']
            else:
                filename = self.config['network'] + str(time.time())
        util.save_network(self.net, filename)

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
        util.printNetwork(self.net)

#======================================================================
#=Internal methods=====================================================
#======================================================================


    def _createNetwork(self):
        if(self.config['outlayer'] == "linear"): layer = LinearLayer
        elif(self.config['outlayer'] == "sigmoid"): layer = SigmoidLayer
        elif(self.config['outlayer'] == "softmax"): layer = SoftmaxLayer
        else: raise Exception("Cannot create network: no output layer specified")
        if(self.config['fast'] != ""):
            fast = True
#             self.net = self.net.convertToFastNetwork()
        else:
            fast = False
        self.net = buildNetwork(INPUTS, self.hidden, self.outneurons, hiddenclass=LSTMLayer, outclass=layer, recurrent=True, outputbias=False, fast=fast)
        self.net.randomize()
        print("LSTM network created: " + self.name)
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