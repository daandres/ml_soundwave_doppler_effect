import numpy as np
import classifier.lstm.util as util

'''
LSTMData class provides data related methods for LSTM module. 
'''
class LSTMData:

    def __init__(self, config, net):
        self.init = True
        self.config = config
        self.net = net
        self.loadData()
        self.init = False

    '''
    Validates the LSTMNet by testing against the testset. Addiditional creates a confmat
    '''
    def validate(self):
        if(self.testds == None):
            print("Can't validate without loaded data")
            return
        print(self.testds.evaluateModuleMSE(self.net.net))
        self.__confmat()

    '''
    saves dataset to file
    '''
    def saveData(self, filename=""):
        if filename == "":
            filename = self.config['dataset']
        util.save_dataset(self.ds, self.testds, self.config['path'] + "data/" + filename)

    '''
    Interface method for data loading. Based on configuration and startup state, data is not 
    loaded, data is loaded from dataset files or created from sample files and splitted into the trainings and testset. 
    At the end the dataset targets are converted to the one of many representation, which encodes a class number by a 1 
    in nClasses of 0, eg. nCLasses = 7; class 3 = [0 0 0 1 0 0 0]. This is better for LSTMNets
    '''
    def loadData(self, filename=""):
        if(self.init):
            if(self.config['autoload_data'] == "true"):
                if(self.config['autoload_dataset'] == "true"):
                    self.__loadDataset(filename)
                else:
                    self.ds = util.createPyBrainDatasetFromSamples(self.net.classes, self.net.nClasses, "", self.config['data_average'], self.config['merge67'], self.net.datacut, self.net.datafold)
                    self.testds, self.ds = self.ds.splitWithProportion(0.2)
                    if(self.config['autosave_dataset'] == "true"):
                        parms = []
                        parms.append("o" + str(self.nClasses))
                        parms.append("c" + str(self.datacut))
                        parms.append("f" + str(self.datafold))
                        self.saveData("_".join(parms))
            else:
                self.testds, self.ds = None, None
                print("No data loaded as configured")
                return
        else:
            self.__loadDataset(filename)
        print("Train sequences " + str(self.ds.getNumSequences()))
        print("Train set: " + str(self.ds.calculateStatistics()))
        print("Test sequences " + str(self.testds.getNumSequences()))
        print("Test set: " + str(self.testds.calculateStatistics()))
        self.ds._convertToOneOfMany(bounds=[0, 1])
        self.testds._convertToOneOfMany(bounds=[0, 1])

    '''
    Loads Dataset from file. If no filename is provided a generated file is searched by using 
    data relevant information (o (nClasses), if the data was cutted (c) and if the data was folded (f)
    Data is loaded under the configured path + /data 
    '''
    def __loadDataset(self, filename=""):
        if filename == "":
            filename = self.config['dataset']
            if filename == "":
                parms = []
                parms.append("o" + str(self.net.nClasses))
                parms.append("c" + str(self.net.datacut))
                parms.append("f" + str(self.net.datafold))
                filename = "_".join(parms)
        self.ds, self.testds = util.load_dataset(self.config['path'] + "data/" + filename)

    '''
    Calculates the confmat based on the testdataset and calculates the error
    
    Altenrative for error calculation, but without confmat:
    trnresult = 100. * (1.0 - testOnSequenceData(self.net, self.testds))
    '''
    def __confmat(self):
        confmat = np.zeros((self.net.nClasses, self.net.nClasses))
        for i in range(self.testds.getNumSequences()):
            self.net.reset()
            sequence = self.testds.getSequence(i)
            target = np.argmax(sequence[1][31])
            out = self.net._activateSequence(sequence[0])
            confmat[target][out] += 1
        sumWrong = 0
        sumAll = 0
        for i in range(self.net.nClasses):
            for j in range(self.net.nClasses):
                if i != j:
                    sumWrong += confmat[i][j]
                sumAll += confmat[i][j]
        error = sumWrong / sumAll
        np.set_printoptions(suppress=True)
        print(confmat)
        print("Validation error: %5.2f%%" % (100. * error))
