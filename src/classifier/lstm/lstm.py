from classifier.classifier import IClassifier
from pybrain.structure import LSTMLayer, LinearLayer, SoftmaxLayer
from pybrain.unsupervised.trainers.deepbelief import DeepBeliefTrainer
from pybrain.supervised.trainers import RPropMinusTrainer, BackpropTrainer
from pybrain.supervised.trainers.evolino import EvolinoTrainer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure.modules.evolinonetwork import EvolinoNetwork
from pybrain.tools.validation import testOnSequenceData
import classifier.lstm.util as util
import numpy as np
from threading import Thread
import time
# import arac

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
OUTPUTS = 1
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
        if(self.config['network_type'] == "gradient" or self.config['network_type'] == "optimization"):
            self.net = buildNetwork(INPUTS, self.hidden, OUTPUTS, hiddenclass=LSTMLayer, outclass=LinearLayer, recurrent=True, outputbias=False)
            self.net.randomize()
#         self.net = self.net.convertToFastNetwork()
        elif(self.config['network_type'] == "evolino"):
            self.net = EvolinoNetwork(OUTPUTS, self.hidden)
        else:
            raise Exception("cannot create network, no network type specified")
        print("LSTM network created with " + str(self.hidden) + " LSTM neurons")
        return

    def startClassify(self):
        self.t = Thread(name=NAME, target=self.start, args=())
        self.t.start()
        return self.t

    def startTraining(self):
        assert self.net != None
        assert self.ds != None

        def getRPropTrainer():
            print("LSTM RPropMinusTrainer Training started")
            trainer = RPropMinusTrainer(self.net, dataset=self.ds, verbose=True)
    #         trainer = BackpropTrainer(self.net, dataset=self.ds, verbose=True)
            return trainer

        def getEvolino():
            print("LSTM Evolino Training started")
            wtRatio = 1. / 3.
            trainer = EvolinoTrainer(
                self.net,
                dataset=self.ds,
                subPopulationSize=20,
                nParents=8,
                nCombinations=1,
                initialWeightRange=(-0.01 , 0.01),
            #    initialWeightRange = ( -0.1 , 0.1 ),
            #    initialWeightRange = ( -0.5 , -0.2 ),
                backprojectionFactor=0.001,
                mutationAlpha=0.001,
            #    mutationAlpha = 0.0000001,
                nBurstMutationEpochs=np.Infinity,
                wtRatio=wtRatio,
                verbosity=2)
            return trainer

        def getOptimizationTrainer():
            task = GoNorthwardTask()
            l = algo(self.ds.evaluateModuleMSE, self.net, verbose=True)
            return l

        def train(training):
            start = time.time()
            print("start training with " + str(self.epochs) + " epochs: " + str(start))
            tenthOfEpochs = self.epochs / 10
            for i in range(10):
                inBetweenStart = time.time()
                training(tenthOfEpochs)
                end = time.time()
                diff = end - inBetweenStart
                print("Training time of epoch " + str(i) + " : " + str(end) + "\nDiff: " + str(diff))
            if(self.epochs - (tenthOfEpochs * 10) > 0):
                training(self.epochs - (tenthOfEpochs * 10))
            end = time.time()
            diff = end - start
            print("Training end: " + str(end) + "\nDiff: " + str(diff))
            if(self.config['autosave_network'] == "true"):
                filename = str(time.time()) + "_n" + str(self.hidden) + "_e" + str(self.epochs) + "_o" + OUTPUTS
                self.save(filename, overwrite=False)
            self.validate()
            return

        #==========
        # =Training=
        if(self.config['network_type'] == "gradient"):
            trainer = getRPropTrainer();
            train(trainer.trainEpochs)
        elif(self.config['network_type'] == "evolino"):
            trainer = getEvolino();
            train(trainer.trainEpochs)
        elif(self.config['network_type'] == "optimization"):
            trainer = getOptimizationTrainer();
            train(trainer.learn)
            return
        else:
            raise Exception("Cannot create trainer, no network type specified")


    def validateOnData(self):
        trnresult = 100. * (1.0 - testOnSequenceData(self.net, self.ds))
        print("Validation error: %5.2f%%" % trnresult)

    def classify(self, data):
        out = self.net.activate(data)
        self.datanum += 1
        if(self.datanum >= 32):
            self.datanum = 0
            self.net.reset()
            print(str(np.argmax(out)) + " " + str(out))

    def startValidation(self):
        self.validate()

    def validate(self):
        self.validateOnData()
#         print(self.ds.evaluateMSE(self.net))
        confmat = np.zeros((NCLASSES, NCLASSES))
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
            # confmat[np.round(target)[0]][np.round(out)[0]] += 1
            print "out:\t", str(out), "\ttarget:\t", str(target)
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
