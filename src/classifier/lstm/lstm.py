from pybrain.datasets import SequenceClassificationDataSet
from pybrain.structure import LSTMLayer, LinearLayer, SoftmaxLayer
from pybrain.supervised.trainers import RPropMinusTrainer, BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.validation import testOnSequenceData
from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.tools.customxml.networkreader import NetworkReader

from threading import Thread
import time
import numpy as np
from src.gestureFileIO import GestureFileIO


INPUTS = 64
HIDDEN = 100
OUTPUTS = 8
TRAINING_EPOCHS = 1
CLASSES = [0, 6, 7]

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

    def startTraining(self, filename, createNew=False, save=False):
        print "LSTM Training started"
        self.net = buildNetwork(INPUTS, HIDDEN, OUTPUTS, hiddenclass=LSTMLayer, outclass=LinearLayer, recurrent=True, outputbias=False)
        self.net.randomize()
        self.ds = self.getTrainingSet(filename, createNew, save)
        print "Data loaded, now create trainer"
#         trainer = RPropMinusTrainer(self.net, dataset=self.ds, verbose=False)
        trainer = BackpropTrainer(self.net, dataset=self.ds, verbose=True)
        print "start training"
        for _ in range(TRAINING_EPOCHS):
            trainer.trainEpochs(TRAINING_EPOCHS)
            trnresult = 100. * (1.0 - testOnSequenceData(self.net, self.ds))
            print "train error: %5.2f%%" % trnresult, "\n"

    def getTrainingSet(self, filename, createNew=False, save=False):
        ds = None
        if createNew:
            self.createPyBrainDatasetFromSamples(save, filename)
        else:
            ds = SequenceClassificationDataSet.loadFromFile(filename)
        return ds

    def createPyBrainDatasetFromSamples(self, save=False, filename=None):
        g = GestureFileIO()
        data = [0] * 8
        for i in CLASSES:
            data[i] = g.getGesture3D(i, [], "../../")
        print "data loaded, now creating dataset"
        ds = SequenceClassificationDataSet(64, OUTPUTS, nb_classes=8)
        for target in CLASSES:
            tupt = self.getTarget(target, OUTPUTS)
            for x in data[target]:
                ds.newSequence()
                for y in x:
                    tup = tuple(y)
                    ds.appendLinked(tup, tupt)
#             self.ds.setField('input', array[:,:-1])
#             self.ds.setField('target', array[:,-1:])
#         print ds
        if save:
            ds.saveToFile(filename)
        return ds

    def getTarget(self, y, dim):
        if y >= dim:
            raise Exception("wrong dimension chosen for target")
        elif y < 0:
            raise Exception("target is negative")
        assert(y >= 0 and y < dim)
        target = np.zeros((dim,))
        target[y] = 1
        return target

    def classify(self):
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

def testLstm():
    start = time.time()
    print str(start), "\tstart "
#     np.set_printoptions(precision=2, threshold=np.nan)
    lstm = LSTM()
#     lstm.createPyBrainDatasetFromSamples(True, "dataset")
    lstm.startTraining("datasettest", True)
    print time.time(), "\tload network "
    lstm.net = NetworkReader.readFrom('lstm.xml')
    print time.time(), "\tstart classify "
    lstm.classify()
    end = time.time()
    print str(end), "\tend "
    print str(end - start), "\tdifftime"
#     NetworkWriter.writeToFile(lstm.net, 'lstm_backprop.xml')

if __name__ == '__main__':
    testLstm()
