'''
Created on 13/01/2014

@author: Benny
'''
import numpy
import os
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score
import subprocess as sp

def normalise(arr, nn_avg):
    ''' normalise each frame '''
    for d in range(len(arr)):
        for dd in range(len(arr[d])):
            arr[d][dd] = (arr[d][dd] / numpy.amax(arr[d][dd])) - nn_avg
    return arr


def preprocess():
    path = "../../../gestures/Benjamin/"

    ''' load and reshape textfile with 18.5khz frequency data '''
    n = numpy.loadtxt(path + "gesture_6/1389637026.txt", delimiter=",")
    n = n.reshape(n.shape[0], 32, n.shape[1] / 32)  # recordingframes
    nn = normalise(n, 0)
    ''' create average of 18.5khz frequency data '''
    nn_avg = numpy.mean(nn, axis=1)
    nn_avg = numpy.mean(nn_avg, axis=0)

    print nn_avg
    return nn_avg


def test(nn_avg):
    path = "../../../gestures/"
    name = "Annalena"
    gesturenumber = 0

    dirf = os.listdir(path + name + "/gesture_" + str(gesturenumber))
    firsttextfile = dirf[0]

    p = path + name + "/gesture_" + str(gesturenumber) + "/" + firsttextfile

    n = numpy.loadtxt(p, delimiter=",")
    n = n.reshape(n.shape[0], 32, n.shape[1] / 32)  # recordingframes
    nn = normalise(n, nn_avg)
    nn = nn.reshape(nn.shape[0], nn.shape[1] * nn.shape[2])

    Y_data = nn  # [10:]
    Y_targets = numpy.zeros(Y_data.shape[0], dtype=int)

    print "Y_data", "\t\t", Y_data.shape
    print "Y_targets", "\t", Y_targets.shape

    return Y_data, Y_targets

def predict_svm(classifier, Y_data, Y_targets):
    Y_pred = classifier.predict(Y_data)
    accuracy = accuracy_score(Y_targets, Y_pred)
    result = str(accuracy * 100)[:5] + "%"
    print "\naccuracy:\t", result

if __name__ == "__main__":
    classifier = joblib.load('svm_trained.pkl')

    nn_avg = preprocess()

    Y_data, Y_targets = test(nn_avg)

    predict_svm(classifier, Y_data, Y_targets)
    
    
def executeCommand(self, number):
    if number != 6:
        
        ''' some switch cases for application execution and termination '''
        if number == 0 and self.executed["notepad"] == False:
            print "\t",str(number),"=>","starting notepad"
            proc = sp.Popen("notepad")
            self.executed["notepad"] = proc.pid

        elif number == 1 and self.executed["notepad"] != False:
            print "\t",str(number),"=>","terminating notepad"
            sp.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.executed["notepad"]), shell=True, stdout=sp.PIPE)
            self.executed["notepad"] = False

        elif number == 2 and self.executed["taskmgr"] == False:
            print "\t",str(number),"=>","starting taskmanager"
            proc = sp.Popen("taskmgr")
            self.executed["taskmgr"] = proc.pid

        elif number == 3 and self.executed["taskmgr"] != False:
            print "\t",str(number),"=>","terminating taskmanager"
            sp.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.executed["taskmgr"]), shell=True, stdout=sp.PIPE)
            self.executed["taskmgr"] = False

        elif number == 4 and self.executed["calc"] == False:
            print "\t",str(number),"=>","starting calculator"
            proc = sp.Popen("calc")
            self.executed["calc"] = proc.pid

        elif number == 5 and self.executed["calc"] != False:
            print "\t",str(number),"=>","terminating calculator"
            sp.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.executed["calc"]), shell=True, stdout=sp.PIPE)
            self.executed["calc"] = False

        
        elif number == 1 and self.executed["notepad"] == False:
            print "\t",str(number),"=>","notepad not started, nothing to terminate"
        elif number == 3 and self.executed["taskmgr"] == False:
            print "\t",str(number),"=>","taskmanager not started, nothing to terminate"
        elif number == 5 and self.executed["calc"] == False:
            print "\t",str(number),"=>","calculator not started, nothing to terminate"
            
        elif number == 0 and self.executed["notepad"] != False:
            print "\t",str(number),"=>","notepad already started, only one instance allowed"
        elif number == 2 and self.executed["taskmgr"] != False:
            print "\t",str(number),"=>","taskmanager already started, only one instance allowed"
        elif number == 4 and self.executed["calc"] != False:
            print "\t",str(number),"=>","calculator already started, only one instance allowed"


