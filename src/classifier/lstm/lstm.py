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
OUTPUTS = 8
NCLASSES = 8
CLASSES = [0, 1, 2, 3, 4, 5, 6, 7]

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

    def startClassify(self):
        self.t = Thread(name="LSTM", target=self.start, args=())
        self.t.start()
        return self.t

    def start(self):
        print "LSTM started"

    def startTraining(self, filename="default", createNew=True, save=False):
        print "LSTM Training started"
        self.net = buildNetwork(INPUTS, self.hidden, OUTPUTS, hiddenclass=LSTMLayer, outclass=LinearLayer, recurrent=True, outputbias=False)
        self.net.randomize()
        self.ds = self.getTrainingSet(filename, createNew, save)
        print "Data loaded, now create trainer"
        trainer = RPropMinusTrainer(self.net, dataset=self.ds, verbose=True)
#         trainer = BackpropTrainer(self.net, dataset=self.ds, verbose=True)
        print "start training"
        trainer.trainEpochs(self.epochs)
        trnresult = 100. * (1.0 - testOnSequenceData(self.net, self.ds))
        print "train error: %5.2f%%" % trnresult, "\n"

    def getTrainingSet(self, filename, createNew=False, save=False):
        ds = None
        if createNew:
            ds = self.createPyBrainDatasetFromSamples(save, filename)
        else:
            ds = SequenceClassificationDataSet.loadFromFile(filename)
        return ds

    def createPyBrainDatasetFromSamples(self, save=False, filename=None):
        np.set_printoptions(precision=2, threshold=np.nan)
        g = GestureFileIO(relative=self.relative)
        data = [0] * 8
        for i in CLASSES:
            data[i] = g.getGesture3D(i, [])
            print "data ", i, " loaded shape: ", np.shape(data[i])
        print "data loaded, now creating dataset"
        ds = SequenceClassificationDataSet(INPUTS, OUTPUTS, nb_classes=NCLASSES)
        for target in CLASSES:
            tupt = self.getTarget(target, OUTPUTS)
            for x in data[target]:
                ds.newSequence()
                for y in x:
                    tup = tuple(y)
                    ds.appendLinked(tup, tupt)
        print "DS entries" , ds.getNumSequences()
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

def testLstm():
    start = time.time()
    print str(start), "\tstart "
#     np.set_printoptions(precision=2, threshold=np.nan)
    import properties.config as c
    conf = c.getInstance("../../").getConfig("lstm")
    lstm = LSTM(config=conf, relative="../../")
#     lstm.createPyBrainDatasetFromSamples(True, "dataset")
    lstm.startTraining("datasettest", True)
    print time.time(), "\tload network "
    lstm.net = NetworkReader.readFrom('lstm_dummy.xml')
    print time.time(), "\tstart validate "
    lstm.validate()
    end = time.time()
    print str(end), "\tend "
    print str(end - start), "\tdifftime"
#     NetworkWriter.writeToFile(lstm.net, 'lstm_backprop.xml')

if __name__ == '__main__':
    testLstm()
