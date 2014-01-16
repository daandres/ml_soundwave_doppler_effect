from classifier.classifier import IClassifier
from pybrain.structure import LSTMLayer, LinearLayer, SoftmaxLayer, SigmoidLayer
from pybrain.supervised.trainers import RPropMinusTrainer, BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.validation import testOnSequenceData
import classifier.lstm.util as util
import numpy as np
from threading import Thread
import time
import arac

# Optimization learners imports
from pybrain.rl.environments.shipsteer.northwardtask import GoNorthwardTask
from pybrain.optimization import *  # @UnusedWildImport
# algo = HillClimber
algo = GA
# algo = MemeticSearch
# algo = NelderMead
# algo = CMAES
# algo = OriginalNES
# algo = ES
# algo = MultiObjectiveGA

INPUTS = 64
NAME = "LSTM"

class LSTM(IClassifier):

    def __init__(self, recorder=None, config=None, relative=""):
#         if recorder == None:
#             raise Exception("No Recorder, so go home")
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
        if(self.config['autoload_data'] == "true"):
            self.loadData()
        else:
            self.ds = util.createPyBrainDatasetFromSamples(self.classes, INPUTS, self.outneurons, "", self.config['data_average'])
        self.avg = util.getAverage()
        if(self.config['autoload_network'] == "true"):
            self.load()
        else:
            self.createNetwork()


    def getName(self):
        return NAME

    def createNetwork(self):
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

    @DeprecationWarning
    def startClassify(self):
        self.t = Thread(name=NAME, target=self.classify, args=())
        self.t.start()
        return self.t

    def startTraining(self):
        assert self.net != None
        assert self.ds != None

        def getRPropTrainer():
            print("LSTM RPropMinusTrainer Training started")
            trainer = RPropMinusTrainer(self.net, dataset=self.ds, verbose=True)
    #         trainer = BackpropTrainer(self.net, dataset=self.ds, verbose=True)
            return trainer, False

        def getOptimizationTrainer():
            print("LSTM Optimization Training started")
            l = algo(self.ds.evaluateModuleMSE, self.net, verbose=True)
            return l, True

        def train(training, returnsNet):
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
            self.validate()
            return

        #==========
        # =Training=
        if(self.trainingType == "gradient"):
            trainer, returnsNet = getRPropTrainer();
            train(trainer.trainEpochs, returnsNet)
        elif(self.trainingType == "optimization"):
            trainer, returnsNet = getOptimizationTrainer();
            train(trainer.learn, returnsNet)
            return
        else:
            raise Exception("Cannot create trainer, no network type specified")


    def validateOnData(self):
        trnresult = 100. * (1.0 - testOnSequenceData(self.net, self.ds))
        print("Validation error: %5.2f%%" % trnresult)

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
        self.validate()

    def validate(self):
        self.validateOnData()
        print(self.ds.evaluateModuleMSE(self.net))
        confmat = np.zeros((self.nClasses, self.nClasses))
#         print("target-out")
        for i in range(self.ds.getNumSequences()):
            self.net.reset()
            out = None
            target = None
            j = 0
            for dataIter in self.ds.getSequenceIterator(i):
                data = dataIter[0]
                target = dataIter[1]
#                 print(str(i) + "\t" + str(j) + "\tbefore activate")
                out = self.net.activate(data)
#                 print(str(i) + "\t" + str(j) + "\tafter activate")
                j += 1
            confmat[np.argmax(target)][np.argmax(out)] += 1
#             print("out:\t" + str(out) + "\ttarget:\t" + str(target))
#             print(str(np.argmax(target)) + "-" + str(np.argmax(out)))
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
        if filename == "":
            filename = self.config['dataset']
        self.ds = util.load_dataset(filename)

    def saveData(self, filename=""):
        if filename == "":
            filename = self.config['dataset']
        util.save_dataset(self.ds, filename)

    def printClassifier(self):
        util.printNetwork(self.net)
        return