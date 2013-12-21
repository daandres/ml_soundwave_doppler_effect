import time
from threading import Thread, Event
from src.classifier.lstm.lstm import LSTM
from visualizer import View

class Console:
    def __init__(self, recorder=None, applicationClose=None, setFileName=None, getFileName=None):
        if recorder == None:
            raise Exception("No Recorder, so go home")
        self.recorder = recorder
        if applicationClose == None:
            raise Exception("No close callback")
        self.applicationClose = applicationClose
        self.key_bindings = {}
        self.bindKeys()
        self.inputEvent = Event()
        self.recordEvent = Event()
        self.threadNum = 0
        self.repeatedRecords = 0
        self.setFileName = setFileName
        self.getFileName = getFileName

    def recordStart(self, key):
        args = key.split()
        fileName = self.getFileName(key[0])
        print "\nRecording now class ", str(key[0]), " to file ", fileName
        if len(args) > 1:
            num = int(args[1])
            self.repeatedRecords = num
        else:
            self.repeatedRecords = 1
        print "\t", self.repeatedRecords, " instances left"
        while self.repeatedRecords > 0:
            self.repeatedRecords -= 1
            print "\tStart recording next instance.\n\t", self.repeatedRecords, " instances left"
            self.recordEvent.clear()
            self.recorder.setRecordClass(key[0], self.callback)
            self.recordEvent.wait()
        print "finished recording"
        self.inputEvent.set()

    def callback(self, recClass):
        self.recordEvent.set()

    def bindKeys(self):
        self.key_bindings['e'] = self.exit
        self.key_bindings['h'] = self.printHelp
        self.key_bindings['v'] = self.view
        self.key_bindings['c'] = self.classifyStart
        self.key_bindings['t'] = self.trainingStart
        self.key_bindings['f'] = self.changeFilename
        self.key_bindings['0'] = self.recordStart
        self.key_bindings['1'] = self.recordStart
        self.key_bindings['2'] = self.recordStart
        self.key_bindings['3'] = self.recordStart
        self.key_bindings['4'] = self.recordStart
        self.key_bindings['5'] = self.recordStart
        self.key_bindings['6'] = self.recordStart
        self.key_bindings['7'] = self.recordStart


    def startNewThread(self):
        self.t = Thread(name="ControlConsole-" + str(self.threadNum), target=self.start, args=())
        self.t.start()
        self.threadNum += 1
        return self.t

    def is_alive(self):
        if self.t is not None:
            return self.t.is_alive()
        return False

    def start(self):
        self.alive = True
        while self.alive:
            txtin = raw_input('> ')
            if txtin[0] not in self.key_bindings:
                print "No command for " + txtin
                continue
            self.inputEvent.clear()
            self.key_bindings[txtin[0]](txtin)
            self.inputEvent.wait()
        return

    def exit(self, txtin):
        self.alive = False
        self.inputEvent.set()
        self.applicationClose()

    def view(self, command):
        self.view = View(self.recorder, self.viewCallback)
        self.view.startNewThread()

    def viewCallback(self, code):
        print "View closed with code ", str(code)
        self.inputEvent.set()

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

    def printHelp(self, args=None):
        printHelp(event=self.inputEvent)

    def changeFilename(self, args=None):
        argsarr = args.split(" ", 2)
        newName = ""
        if len(argsarr) > 1:
            newName = argsarr[1]
        else:
            newName = str(time.time())[:-3]
        self.setFileName(newName)
        self.inputEvent.set()

def printHelp(args=None, event=None):
    print "Gesture Recognition based on the Soundwave doppler effect"
    print "Supported classifiers: svm, trees, hmm, k-means and lstm"
    print "Usage: <command> [<option>]"
    print "<digit> [<digit>]\t0-7 record a gesture and associate with class number [repeat <digit> times]"
    print "c <classifier> \tstart real time classifying with the specified classifier"
    print "t <classifier> \tstart training for the specified classifier with the saved data"
    print "e \t\texit application"
    print "v \t\tstart view"
    print "f [<string>] \tchange filename for recording. if empty use current time "
    print "h \t\tprint this help"
    print ""
    print "0 Right-To-Left-One-Hand\n1 Top-to-Bottom-One-Hand\n2 Entgegengesetzt with two hands\n3 Single-push with one hand\n4 Double-push with one hand\n5 Rotate one hand\n6 Background noise (no gesture, but in silent room)\n7 No gesture with background sound (in a Pub, at office, in the kitchen, etc.)"
    print ""
    if event is not None:
        event.set()
