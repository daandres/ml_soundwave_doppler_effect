class IClassifier:
    def getName(self):
        pass
    def startClassify(self):
        pass
    def startTraining(self, filename="default", createNew=True, save=False):
        pass
    def classify(self, data):
        pass
    def startValidation(self):
        pass
    def load(self, filename=""):
        pass
    def save(self, filename=""):
        pass