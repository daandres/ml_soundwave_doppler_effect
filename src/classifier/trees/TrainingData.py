'''
Created on 05.02.2014

@author: Annalena
'''

class TrainingData(object):
    '''
    classdocs
    '''


    def __init__(self):
        self.gestures = self.classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_2/1391437451.txt")
        self.gestures += self.classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_2/1391437809.txt")
        self.gestures += self.classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_3/1391439011.txt")
        self.gestures += self.classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_3/1391439281.txt")
        self.gestures += self.classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_4/1391439536.txt")
        self.gestures += self.classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_4/1391439659.txt")
        #gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_0/1391435081.txt")
        #gestures += classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_0/1391435669.txt")
        self.gestures += self.classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_1/1391436572.txt")
        self.gestures += self.classifier.trees.ProcessData.getTestData("../gestures/Annalena/gesture_1/1391436738.txt")
        self.gestures += self.classifier.trees.ProcessData.getTestData("../gestures/Daniel/gesture_6/gesture_6_zimmer_1.txt")
        self.gestures += self.classifier.trees.ProcessData.getTestData("../gestures/Daniel/gesture_6/gesture_6_zimmer_3.txt")
       
       
    def getData(self):
        pass
    
    def getTargets(self):
        pass