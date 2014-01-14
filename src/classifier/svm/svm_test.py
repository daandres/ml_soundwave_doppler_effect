'''
Created on 13/01/2014

@author: Benny
'''
import numpy
import os
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score


def normalise(arr,nn_avg):
    ''' normalise each frame '''
    for d in range(len(arr)):
        for dd in range(len(arr[d])):
            arr[d][dd] = (arr[d][dd]/numpy.amax(arr[d][dd]))-nn_avg
    return arr

   
def preprocess():
    path = "../../../gestures/Benjamin/"
    
    ''' load and reshape textfile with 18.5khz frequency data '''
    n = numpy.loadtxt(path+"gesture_6/1389637026.txt",delimiter=",")
    n = n.reshape(n.shape[0],32,n.shape[1]/32) #recordingframes
    nn = normalise(n,0)
    ''' create average of 18.5khz frequency data '''
    nn_avg = numpy.mean(nn, axis=1)
    nn_avg = numpy.mean(nn_avg, axis=0)

    
    return nn_avg


def test(nn_avg):
    path = "../../../gestures/"
    name = "Annalena"
    gesturenumber = 0
    
    dirf = os.listdir(path+name+"/gesture_"+str(gesturenumber))
    firsttextfile = dirf[0]
    
    p = path+name+"/gesture_"+str(gesturenumber)+"/"+firsttextfile
    
    n = numpy.loadtxt(p,delimiter=",")
    n = n.reshape(n.shape[0],32,n.shape[1]/32) #recordingframes
    nn = normalise(n,nn_avg)
    nn = nn.reshape(nn.shape[0],nn.shape[1]*nn.shape[2])
    
    Y_data = nn#[10:]
    Y_targets = numpy.zeros(Y_data.shape[0], dtype=int)
    
    print "Y_data", "\t\t", Y_data.shape
    print "Y_targets", "\t", Y_targets.shape
    
    return Y_data, Y_targets

def predict_svm(classifier, Y_data, Y_targets):
    Y_pred = classifier.predict(Y_data)
    accuracy = accuracy_score(Y_targets, Y_pred)
    result = str(accuracy*100)[:5]+"%"
    print "\naccuracy:\t", result

if __name__ == "__main__":
    classifier = joblib.load('svm_trained.pkl')
    
    nn_avg = preprocess()
    
    Y_data, Y_targets = test(nn_avg)
    
    predict_svm(classifier, Y_data, Y_targets)
    