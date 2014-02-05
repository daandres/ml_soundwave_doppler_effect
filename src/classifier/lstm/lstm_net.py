import numpy as np
from pybrain.structure import LSTMLayer, LinearLayer, SoftmaxLayer, SigmoidLayer
from pybrain.tools.shortcuts import buildNetwork
import classifier.lstm.util as util
import time

'''
LSTMNet holds the LSTM network and provides related methods. Also it holds parameters defined in config or parsed by network name. 
'''
class LSTMNet:

    def __init__(self, config):
        self.config = config

        self.customName = self.config['customname']
        self.hidden = int(self.config['hiddenneurons'])
        self.layer = self.config['outlayer']
        self.peepholes = bool(self.config['peepholes'])
        self.classes = eval(self.config['classes'])
        self.nClasses = len(self.classes)
        self.datacut = int(self.config['data_cut'])
        self.datafold = int(self.config['data_fold'])
        self.trainingType = self.config['training']
        self.epochs = int(self.config['trainingepochs'])
        self.trainedEpochs = 0

        self.inputdim = np.ceil((64 - 2 * self.datacut) / self.datafold)


        if(self.config['autoload_network'] == "true"):
            self.load()
        else:
            self._createNetwork()
        pass

    '''
    Creates a new LSTM Network with configured parameters and initialze its weights randomly. 
    '''
    def _createNetwork(self):
        if(self.layer == "linear"): layer = LinearLayer
        elif(self.layer == "sigmoid"): layer = SigmoidLayer
        elif(self.layer == "softmax"): layer = SoftmaxLayer
        else: raise Exception("Cannot create network: no output layer specified")
        self.net = buildNetwork(self.inputdim, self.hidden, self.nClasses, hiddenclass=LSTMLayer, outclass=layer, recurrent=True, outputbias=False, peepholes=self.peepholes)
        self.net.randomize()
        print("LSTM network created: " + self.getName())
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
    Interface method to reset the internal state of the network
    '''
    def reset(self):
        self.net.reset()

    '''
    Loads a network from file and sets the parameter from the filename. 
    '''
    def load(self, filename=""):
        if filename == "":
            filename = self.config['network']
        self.net = util.load_network(self.config['path'] + "networks/" + filename)
        self.net.sorted = False
        self.net.sortModules()
        netValues = util.parseNetworkFilename(filename)
        for key, value in netValues.items():
            if(key == 'neurons'):
                self.hidden = int(value)
            elif(key == 'layer'):
                self.layer = value
            elif(key == 'peepholes'):
                if(value == 'True'):
                    self.peepholes = True
                else:
                    self.peepholes = False
            elif(key == 'nClasses'):
                self.nClasses = int(value)
            elif(key == 'datacut'):
                self.datacut = int(value)
            elif(key == 'datafold'):
                self.datafold = int(value)
            elif(key == 'trainer'):
                self.trainingType = value
            elif(key == 'epochs'):
                self.trainedEpochs = int(value)

    '''
    saves a network to file
    '''
    def save(self, filename="", overwrite=True):
        if filename == "":
            if overwrite:
                filename = self.config['network']
            else:
                filename = self.config['network'] + str(time.time())
        util.save_network(self.net, self.config['path'] + "networks/" + filename)

    '''
    returns the name of the network by specifing all relevant data to reconstruct the network except the weights
    '''
    def getName(self):
        parms = []
        if(self.customName != ""):
            parms.append(self.customName)
        parms.append("n" + str(self.hidden))
        parms.append("l" + self.layer)
        parms.append("p" + str(self.peepholes))
        parms.append("o" + str(self.nClasses))
        parms.append("c" + str(self.datacut))
        parms.append("f" + str(self.datafold))
        parms.append("t" + self.trainingType)
        parms.append("e" + str(self.trainedEpochs))
        return "_".join(parms)

    '''
    Print network modules and weights
    '''
    def printNetwork(self):
        print(self.getName())
        util.printNetwork(self.net)
