'''
Created on 07/01/2014

@author: Benny
'''
import numpy
from sklearn import svm
from sklearn import cross_validation
from sklearn.metrics import accuracy_score

if True:
    import mouth

def train_svm(X_train, Y_train, X_test, Y_test, c, gamma, method, cv):
    
    ''' Initialise the model with best model parameters reported at '''
    ''' http://peekaboo-vision.blogspot.co.uk/2010/09/mnist-for-ever.html '''
    print "...initialising svm"
    classifier = svm.SVC(kernel="rbf", C=c, gamma=gamma)
    
    ''' Train and validate the classifier '''
    if method == "fit":   
        print "...performing normal fitting"
        classifier.fit(X_train, Y_train)  
        Y_pred = classifier.predict(X_test)
        accuracy = accuracy_score(Y_test, Y_pred)
        result = str(accuracy*100)[:5]+"%"
        
    if method == "cross":
        print "...performing cross-validation"
        accuracy = cross_validation.cross_val_score(classifier, X_train, Y_train, cv=cv)
        result = str(numpy.average(accuracy)*100)[:5]+"%"
        
    print "\naccuracy:\t", result
    
def normalise(arr):
    ''' normalise each frame '''
    for d in range(len(arr)):
        for dd in range(len(arr[d])):
            arr[d][dd] = arr[d][dd]/numpy.amax(arr[d][dd])
    return arr

    
def preprocess():
    ''' load and reshape textfile with 20khz frequency data '''
    n = numpy.loadtxt("../gestures/Benjamin/20khz_frequency.txt",delimiter=",")
    n = n.reshape(n.shape[0],32,n.shape[1]/32) #recordingframes
    
    ''' load and reshape textfile with gesture data '''
    g = numpy.loadtxt("../gestures/Benjamin/test_gesture.txt",delimiter=",")
    g = g.reshape(g.shape[0],32,g.shape[1]/32) #recordingframes
    
    ''' normalise data '''
    nn = normalise(n)
    gn = normalise(g)
    
    ''' create average of 20khz frequqncy data '''
    nn_avg = numpy.mean(nn, axis=1)
    nn_avg = numpy.mean(nn_avg, axis=0)
    
    return nn_avg, gn
    
if __name__ == "__main__":
    c = 100
    gamma = 10
    cv = 3                                     # n times cross-validation
    method = "fit"                             # "fit" or "cross"
    
    train_svm(X_train, Y_train, X_test, Y_test)