import sys
from threading import Thread
from src.classifier.lstm.lstm import LSTM, testLstm

class Console:
    def __init__(self, recorder=None, applicationClose=None):
        if recorder == None:
            raise Exception("No Recorder, so go home")
        self.recorder = recorder
        if applicationClose==None:
            raise Exception("No close callback")
        self.applicationClose = applicationClose
        self.key_bindings = {}
        self.bindKeys()
        
    def recordStart(self, key):
        self.alive = False
        self.recorder.setRecordClass(key, self.callback)

    def bindKeys(self):
        self.key_bindings['0'] = self.recordStart
        self.key_bindings['1'] = self.recordStart
        self.key_bindings['2'] = self.recordStart
        self.key_bindings['3'] = self.recordStart
        self.key_bindings['4'] = self.recordStart
        self.key_bindings['5'] = self.recordStart
        self.key_bindings['6'] = self.recordStart
        self.key_bindings['7'] = self.recordStart
        self.key_bindings['c lstm'] = self.classifyStart
        self.key_bindings['classify lstm'] = self.classifyStart
        self.key_bindings['t lstm'] = self.trainingStart
        self.key_bindings['train lstm'] = self.trainingStart
             
    def callback(self, recClass):
        print "Recording finished for class " + str(recClass)
        self.startNewThread()
    
    def startNewThread(self):
        self.t = Thread(name="ControlConsole", target=self.start, args=())
        self.t.start()
        return self.t
    
    def is_alive(self):
        if self.t is not None:
            return self.t.is_alive()
        return False
    
    def start(self):    
        self.alive = True
        while self.alive:
            input = raw_input('> ')
            if input != 'exit':
                if input not in self.key_bindings:
                    print "No command for " + input
                    continue
                self.key_bindings[input](input)
            else:
                self.alive = False
                self.applicationClose()
                
            
    def close(self):
        self.recorder.close()
        sys.exit()
        
    def classifyStart(self, key):
        method = key.split()[1]
        # TODO do it better... switch case, exception handling, ...
        if(method == 'lstm'):
            classificator = LSTM(self.recorder)
        classificator.startNewThread()
        
    def trainingStart(self, key):
        method = key.split()[1]
        # TODO do it better... switch case, exception handling, ...
        if(method == 'lstm'):
            classificator = LSTM(self.recorder)
        classificator.startTraining()
        
