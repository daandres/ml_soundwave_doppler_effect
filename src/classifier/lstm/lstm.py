from classifier.classifier import IClassifier
from pybrain.structure import LSTMLayer, LinearLayer, SoftmaxLayer
from pybrain.supervised.trainers import RPropMinusTrainer, BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.validation import testOnSequenceData
import classifier.lstm.util as util
import numpy as np
from threading import Thread
import time
# import arac

INPUTS = 64
OUTPUTS = 8
NCLASSES = 8
CLASSES = [0, 1, 2, 3, 4, 5, 6, 7]
NAME = "LSTM"

class LSTM(IClassifier):

    def __init__(self, recorder=None, config=None, relative=""):
#         if recorder == None:
#             raise Exception("No Recorder, so go home")
        self.recorder = recorder
        self.config = config
        self.hidden = int(self.config['hiddenneurons'])
        self.epochs = int(self.config['trainingepochs'])
        self.datanum = 0
        self.relative = relative
        if(self.config['autoload_data'] == "true"):
            self.loadData()
        else:
            self.ds = util.createPyBrainDatasetFromSamples(CLASSES, INPUTS, OUTPUTS, "")
        if(self.config['autoload_network'] == "true"):
            self.load()
        else:
            self.createNetwork()

    def getName(self):
        return NAME

    def createNetwork(self):
        self.net = buildNetwork(INPUTS, self.hidden, OUTPUTS, hiddenclass=LSTMLayer, outclass=LinearLayer, recurrent=True, outputbias=False)
        self.net.randomize()
#         self.net = self.net.convertToFastNetwork()
        print("LSTM network created with " + str(self.hidden) + " LSTM neurons")
        return

    def startClassify(self):
        self.t = Thread(name=NAME, target=self.start, args=())
        self.t.start()
        return self.t

    def startTraining(self):
        assert self.net != None
        assert self.ds != None
        print("LSTM RPropMinusTrainer Training started")
        trainer = RPropMinusTrainer(self.net, dataset=self.ds, verbose=True)
#         trainer = BackpropTrainer(self.net, dataset=self.ds, verbose=True)
        start = time.time()
        print("start training with " + str(self.epochs) + " epochs: " + str(start))
        tenthOfEpochs = self.epochs / 10
        for _ in range(10):
            inBetweenStart = time.time()
            trainer.trainEpochs(tenthOfEpochs)
            end = time.time()
            diff = end - inBetweenStart
            print("Training time: " + str(end) + "\nDiff: " + str(diff))
        if(self.epochs - (tenthOfEpochs * 10) > 0):
            trainer.trainEpochs(self.epochs - (tenthOfEpochs * 10))
        end = time.time()
        diff = end - start
        print("Training end: " + str(end) + "\nDiff: " + str(diff))
        if(self.config['autosave_network'] == "true"):
            self.save(overwrite=False)
        self.validate()
        return

    def validateOnData(self):
        trnresult = 100. * (1.0 - testOnSequenceData(self.net, self.ds))
        print("Validation error: %5.2f%%" % trnresult)

    def classify(self, data):
        out = self.net.activate(data)
        self.datanum += 1
        if(self.datanum >= 32):
            self.datanum = 0
            self.net.reset()
            print(np.argmax(out))

    def startValidation(self):
        self.validate()

    def validate(self):
        self.validateOnData()
#         print(self.ds.evaluateMSE(self.net))
        confmat = np.zeros((OUTPUTS, OUTPUTS))
        for i in range(self.ds.getNumSequences()):
            self.net.reset()
            out = None
            target = None
            for dataIter in self.ds.getSequenceIterator(i):
                data = dataIter[0]
                target = dataIter[1]
                out = self.net.activate(data)
            confmat[np.argmax(target)][np.argmax(out)] += 1
#                 print("target:\t", np.argmax(target)
#                 print("out:\t", np.argmax(out)
#                 print(""
        sumWrong = 0
        sumAll = 0
        for i in range(OUTPUTS):
            for j in range(OUTPUTS):
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
