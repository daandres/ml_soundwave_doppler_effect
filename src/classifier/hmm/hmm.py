from classifier.classifier import IClassifier
import numpy as np
from threading import Thread
import time

NAME = "HiddenMarkovModel"

class HMM(IClassifier):

    def __init__(self, recorder=None, config=None, relative=""):
        self.recorder = recorder
        self.config = config
        self.relative = relative


    def getName(self):
        return NAME


    def startClassify(self):
        pass


    def startTraining(self):
        pass


    def classify(self, data):
        pass


    def startValidation(self):
        pass


    def load(self, filename=""):
        pass


    def save(self, filename=""):
        pass


    def loadData(self, filename=""):
        pass


    def saveData(self, filename=""):
        pass
