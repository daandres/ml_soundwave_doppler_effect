import sys
from threading import Thread

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
            key = raw_input('> ')
            if key != 'c':
                if key not in self.key_bindings:
                    print "No command for " + key
                    continue
                self.key_bindings[key](key)
            else:
                self.alive = False
                self.applicationClose()
                
            
    def close(self):
        self.recorder.close()
        sys.exit()
