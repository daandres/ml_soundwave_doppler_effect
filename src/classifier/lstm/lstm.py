from pybrain.structure import LSTMLayer, LinearLayer, SoftmaxLayer
from pybrain.supervised.trainers import RPropMinusTrainer, BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.validation import testOnSequenceData
import src.classifier.lstm.util as util
import numpy as np
from threading import Thread
import time

INPUTS = 64
OUTPUTS = 8
NCLASSES = 8
CLASSES = [0, 1, 2, 3, 4, 5, 6, 7]
NAME = "LSTM"

class LSTM:

    def __init__(self, recorder=None, config=None, relative=""):
#         if recorder == None:
#             raise Exception("No Recorder, so go home")
        self.recorder = recorder
        self.config = config
        self.hidden = int(self.config['hiddenneurons'])
        self.epochs = int(self.config['trainingepochs'])
        self.datanum = 0
        self.relative = relative

    def getName(self):
        return NAME

    def startClassify(self):
        self.t = Thread(name=NAME, target=self.start, args=())
        self.t.start()
        return self.t

    def start(self):
        print "LSTM started"

    def startTraining(self, filename="default", createNew=True, save=False):
        print "LSTM Training started"
        self.net = buildNetwork(INPUTS, self.hidden, OUTPUTS, hiddenclass=LSTMLayer, outclass=LinearLayer, recurrent=True, outputbias=False)
        self.net.randomize()
        self.ds = util.getTrainingSet(CLASSES, INPUTS, OUTPUTS, filename, createNew, save)
        print "Data loaded, now create trainer"
        trainer = RPropMinusTrainer(self.net, dataset=self.ds, verbose=True)
#         trainer = BackpropTrainer(self.net, dataset=self.ds, verbose=True)
        print "start training"
        trainer.trainEpochs(self.epochs)
        trnresult = 100. * (1.0 - testOnSequenceData(self.net, self.ds))
        print "train error: %5.2f%%" % trnresult, "\n"

    def classify(self, data):
        out = self.net.activate(data)
        self.datanum += 1
        if(self.datanum >= 32):
            self.datanum = 0
            self.net.reset()
            print np.argmax(out)

    def startValidation(self):
        self.validate()

    def validate(self):
#         print self.ds.evaluateModuleMSE(self.net)
        confmat = np.zeros((OUTPUTS, OUTPUTS))
        for i in range(self.ds.getNumSequences()):
            for dataIter in self.ds.getSequenceIterator(i):
                self.net.reset()
                out = None
                target = None
                for data in dataIter:
                    target = data
                    out = self.net.activate(data[0])
                confmat[np.argmax(target)][np.argmax(out)] += 1
#                 print "target:\t", np.argmax(target)
#                 print "out:\t", np.argmax(out)
#                 print ""
        print confmat

    def load(self, filename=""):
        if filename == "":
            filename = self.config['network']
        self.net, self.ds = util.load(filename)

    def save(self, filename=""):
        if filename == "":
            filename = self.config['network']
        util.save(self.net, self.ds, filename)
