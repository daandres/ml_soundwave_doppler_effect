from classifier.classifier import IClassifier

from classifier.lstm.lstm_net import LSTMNet
from classifier.lstm.lstm_classify import LSTMClassify
from classifier.lstm.lstm_data import LSTMData
from classifier.lstm.lstm_train import LSTMTrain

NAME = "LSTM"


'''
The LSTM class implements the IClassifier interface and is the interface for the apoplication to the lstm module. 
It holds references to the four LSTMType classes: LSTMNet, LSTMData, LSTM,Train and LSTMClassify and calls them when necessary
'''
class LSTM(IClassifier):

    def __init__(self, recorder=None, config=None, relative=""):
        self.net = LSTMNet(config)
        self.data = LSTMData(config, self.net)
        self.train = LSTMTrain(config, self.net, self.data)
        self.classifier = LSTMClassify(config, self.net)

#======================================================================
#=Interface methods====================================================
#======================================================================

    def getName(self):
        return NAME

    def startTraining(self, args=[]):
        self.train.train(args)

    def classify(self, data):
        self.classifier.classify(data)

    def startValidation(self):
        self.data.validate()

    def load(self, filename=""):
        self.net.load(filename)

    def save(self, filename="", overwrite=True):
        self.net.save(filename, overwrite)

    def loadData(self, filename=""):
        self.data.loadData(filename)

    def saveData(self, filename=""):
        self.data.saveData(filename)

    def printClassifier(self):
        self.net.printNetwork()
