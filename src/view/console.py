import time
from threading import Thread, Event
from visualizer import View
import properties.config as c


class Console:
    def __init__(self, recorder=None, soundplayer=None, applicationClose=None, setFileName=None, getFileName=None):
        if recorder == None:
            raise Exception("No Recorder, so go home")
        self.recorder = recorder
        if soundplayer == None:
            raise Exception("No Soundplayer, so go home")
        self.soundplayer = soundplayer
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
        self.classificators = {}
        self.classificator = None
        self.loadUserConfig()

    def loadUserConfig(self):
        self.userConfig = c.getInstance().getConfig("user")
        print("Hello " + self.userConfig['name'])
        print("Use command 'h' for usage help!")
        self.selectClassifier(["u", self.userConfig['classifier']])
        self.sound = not bool(self.userConfig['autostart_sound'])
        self.soundFirstTime = True
        self.toggleSound("")

    def getClassificator(self, name):
        if(name == ""):
            raise Exception("No classificator specified")
        elif(name == "lstm"):
            if(name not in self.classificators):
                from classifier.lstm.lstm import LSTM
                lstmConfig = c.getInstance().getConfig("lstm")
                cl = LSTM(self.recorder, lstmConfig)
                self.classificators[name] = cl
            cl = self.classificators[name]
            return cl
        elif(name == "svm"):
            if(name not in self.classificators):
                from classifier.svm.svm import SVM
                svmConfig = c.getInstance().getConfig("svm")
                cl = SVM(self.recorder, svmConfig)
                self.classificators[name] = cl
            cl = self.classificators[name]
            return cl

    def recordStart(self, args):
        fileName = self.getFileName(args[0])
        print("\nRecording now class " + str(args[0]) + " to file " + fileName)
        if len(args) > 1:
            num = int(args[1])
            self.repeatedRecords = num
        else:
            self.repeatedRecords = 1
        print("\t" + str(self.repeatedRecords) + " instances left")
        while self.repeatedRecords > 0:
            self.repeatedRecords -= 1
            print("\tStart recording next instance.\n\t" + str(self.repeatedRecords) + " instances left")
            self.recordEvent.clear()
            self.recorder.setRecordClass(args[0], self.callback)
            self.recordEvent.wait()
        print("finished recording")
        self.inputEvent.set()

    def callback(self, recClass):
        self.recordEvent.set()

    def bindKeys(self):
        self.key_bindings['e'] = self.exit
        self.key_bindings['h'] = self.printHelp
        self.key_bindings['g'] = self.view
        self.key_bindings['u'] = self.selectClassifier
        self.key_bindings['c'] = self.classifyStart
        self.key_bindings['t'] = self.trainingStart
        self.key_bindings['v'] = self.validateStart
        self.key_bindings['l'] = self.load
        self.key_bindings['s'] = self.save
        self.key_bindings['f'] = self.changeFilename
        self.key_bindings['r'] = self.toggleSound
        self.key_bindings['p'] = self.printClassifier
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

    def toggleSound(self, args):
        self.sound = not self.sound
        if(self.sound):
            self.soundplayer.setup()
            self.recorder.setup()
            self.soundplayer.startNewThread()
            self.recorder.startNewThread()
            print("Soundplaying and recording started")
            self.soundFirstTime = False
        else:
            if(not self.soundFirstTime):
                self.recorder.close()
                self.soundplayer.stopPlaying()
                self.recorder.thread.join()
                self.soundplayer.t.join()
                print("Soundplaying and recording stopped")
        self.inputEvent.set()

    def start(self):
        self.alive = True
        while self.alive:
            try:
                txtin = raw_input('> ')
                args = txtin.split(" ")
                if args[0] not in self.key_bindings:
                    print("No command for " + args[0])
                    continue
                self.inputEvent.clear()
                self.key_bindings[args[0]](args)
                self.inputEvent.wait()
            except EOFError:
                print("End of File Exception")
                self.alive = False
            except KeyboardInterrupt:
                print("KeyboardInterrupt. Stopping current task (no guarantees for failures), if possible...")
                self.interrupt()
        return

    def exit(self, txtin):
        self.alive = False
        self.inputEvent.set()
        self.applicationClose()

    def view(self, command):
        self.view = View(self.recorder, self.viewCallback)
        self.view.startNewThread()

    def viewCallback(self, code):
        print("View closed with code " + str(code))
        self.inputEvent.set()

    def classifyStart(self, key):
        if self.classificator is None:
            print("No classifier specified")
            self.inputEvent.set()
            return
        self.recorder.classifyStart(self.classificator, self.classifyCallback)
        # no input event set because this done in recorder in another thread

    def classifyCallback(self):
        # only for checking for new Interrupts
        pass

    def selectClassifier(self, args):
        # TODO do it better... switch case, exception handling, ...
        if(args[1] == 'lstm'):
            self.classificator = self.getClassificator(args[1])
            print("Using now classificator " + self.classificator.getName())
        elif(args[1] == 'svm'):
            self.classificator = self.getClassificator(args[1])
            print("Using now classificator " + self.classificator.getName())
        else:
            print("No classifier specified")
        self.inputEvent.set()

    def trainingStart(self, args):
        if self.classificator is None:
            print("No classifier specified")
            self.inputEvent.set()
            return
        self.classificator.startTraining(args)
        self.inputEvent.set()

    def validateStart(self, args):
        if self.classificator is None:
            print("No classifier specified")
            self.inputEvent.set()
            return
        self.classificator.startValidation()
        self.inputEvent.set()

    def load(self, args):
        if self.classificator is None:
            print("No classifier specified")
            self.inputEvent.set()
            return
        filename = ""
        if len(args) > 2:
            filename = args[2]
            if args[1] == "ds":
                self.classificator.loadData(filename)
            else:
                self.classificator.load(filename)
        elif len(args) > 1:
            filename = args[1]
            self.classificator.load(filename)
        self.inputEvent.set()

    def save(self, args):
        if self.classificator is None:
            print("No classifier specified")
            self.inputEvent.set()
            return
        filename = ""
        if len(args) > 2:
            filename = args[2]
            if args[1] == "ds":
                self.classificator.saveData(filename)
            else:
                self.classificator.save(filename)
        elif len(args) > 1:
            filename = args[1]
            self.classificator.save(filename)
        self.inputEvent.set()

    def printClassifier(self, args):
        if self.classificator is None:
            print("No classifier specified")
            self.inputEvent.set()
            return
        self.classificator.printClassifier()
        self.inputEvent.set()

    def printHelp(self, args=None):
        printHelp()
        self.inputEvent.set()

    def changeFilename(self, args):
        newName = ""
        if len(args) > 1:
            newName = args[1]
        else:
            newName = str(time.time())[:-3]
        self.setFileName(newName)
        self.inputEvent.set()

    def interrupt(self):
        self.recorder.classifyStop()
        self.inputEvent.set()

def printHelp(args=None):
    print("Gesture Recognition based on the Soundwave doppler effect")
    print("Usage: <command> [<option>]")
    print("<num> [<num>]\t0-7 record a gesture and associate with class number [repeat <digit> times]")
    print("u <classifier> \tconfigure classifier to use. Supported classifiers: [svm, trees, hmm, k-means, lstm]")
    print("c \t\tstart real time classifying with the configured classifier")
    print("t \t\tstart training for the configured classifier with the saved data")
    print("l <filename> \tload configured classifier and dataset from file")
    print("s [<filename>] \tsave configured classifier and dataset to file with filename or timestamp")
    print("v \t\tstart validation for the configured classifier with the saved data")
    print("e \t\texit application")
    print("g \t\tstart view [BUG: works only one time per runime]")
    print("f [<string>] \tchange filename for recording. if empty use current time ")
    print("r \t\tstart/stop sound playing and recording")
    print("h \t\tprint(this help")
    print("")
    print("0 Right-To-Left-One-Hand\n1 Top-to-Bottom-One-Hand\n2 Entgegengesetzt with two hands\n3 Single-push with one hand\n4 Double-push with one hand\n5 Rotate one hand\n6 Background noise (no gesture, but in silent room)\n7 No gesture with background sound (in a Pub, at office, in the kitchen, etc.)")
    print("")
