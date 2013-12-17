from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import RPropMinusTrainer
from pybrain.datasets import SequenceClassificationDataSet
from pybrain.structure import SoftmaxLayer
from pybrain.structure import LSTMLayer
from pybrain.tools.validation    import testOnSequenceData

import itertools
import numpy as np

from threading import Thread

from src.gestureFileIO import GestureFileIO

INPUTS = 64
HIDDEN = 100
OUTPUTS = 1

class LSTM:
    
    def __init__(self, recorder=None):
#         if recorder == None:
#             raise Exception("No Recorder, so go home")
        self.recorder = recorder
    
    def startNewThread(self):
        self.t = Thread(name="LSTM", target=self.start, args=())
        self.t.start()
        return self.t
    
    def start(self):
        print "LSTM started"
        
    def startTraining(self):
        print "LSTM Training started"
        self.net = buildNetwork(INPUTS, HIDDEN, OUTPUTS, hiddenclass=LSTMLayer, outclass=SoftmaxLayer, recurrent=True, outputbias=False) 
        self.net.randomize()
        self.ds = self.getTrainingSet()
        trainer = RPropMinusTrainer(self.net, dataset=self.ds, verbose=True)
        for _ in range(10):
            trainer.trainEpochs(2)
            trnresult = 100. * (1.0 - testOnSequenceData(self.net, self.ds))
            print "train error: %5.2f%%" % trnresult, "\n"
 
    def getTrainingSet(self):
        g = GestureFileIO()
        data = [0] * 6
        for i in range(5):
            data[i] = g.getGesture3D(i, ["Daniel"], "../../")
        ds = SequenceClassificationDataSet(64, 1, nb_classes=8)
        for target in range(5):
            tupt = (target,)
            for x in data[target]:
                ds.newSequence()
                for y in x:
                    tup = tuple(y)
                    ds.appendLinked(tup, tupt)
        print ds
        return ds
    
    def classify(self):
        for i in self.ds:
            out = self.net.activate(0.5)
            print out
    
lstm = LSTM()
lstm.startTraining()
lstm.classify()

