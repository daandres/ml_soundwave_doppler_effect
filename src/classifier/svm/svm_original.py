'''
Created on 07/01/2014

@author: Benny
'''
import os
import numpy
from sklearn import svm
from sklearn import cross_validation
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib


def train_svm(X_train, Y_train, X_test, Y_test, c, gamma, method, cv, degree, coef0, kernel):

    ''' Initialise the model with best model parameters reported at '''
    ''' http://peekaboo-vision.blogspot.co.uk/2010/09/mnist-for-ever.html '''
    print "...initialising svm"
    classifier = svm.SVC(kernel=kernel, C=c, gamma=gamma, degree=degree, coef0=coef0)

    ''' Train and validate the classifier '''
    if method == "fit":
        print "...performing normal fitting"
        classifier.fit(X_train, Y_train)
        Y_pred = classifier.predict(X_test)
        accuracy = accuracy_score(Y_test, Y_pred)
        result = str(accuracy * 100)[:5] + "%"

    if method == "cross":
        print "...performing cross-validation"
        accuracy = cross_validation.cross_val_score(classifier, X_train, Y_train, cv=cv)
        result = str(numpy.average(accuracy) * 100)[:5] + "%"

    joblib.dump(classifier, 'svm_trained.pkl', compress=9)

    print "\naccuracy:\t", result

def normalise(arr, nn_avg):
    ''' normalise each frame '''
    for d in range(len(arr)):
        for dd in range(len(arr[d])):
            arr[d][dd] = (arr[d][dd] / numpy.amax(arr[d][dd])) - nn_avg
    return arr


def preprocess():
    names = ["Alex", "Benjamin", "Daniel", "Frank"]
    # names = ["Alex", "Annalena", "Daniel", "Benjamin"]
    path = "../../../gestures/"
    threshold = 0.1

    ''' load and reshape textfile with 18.5khz frequency data '''
    n = numpy.loadtxt(path + "Benjamin/gesture_6/1389637026.txt", delimiter=",")
    n = n.reshape(n.shape[0], 32, n.shape[1] / 32)  # recordingframes
    nn = normalise(n, 0)
    ''' create average of 18.5khz frequency data '''
    nn_avg = numpy.mean(nn, axis=1)
    nn_avg = numpy.mean(nn_avg, axis=0)
    # print nn_avg.shape


    gestures = []
    targets = []
    for gesturenumber in range(7):

        for name in names:
            dirf = os.listdir(path + name + "/gesture_" + str(gesturenumber))
            # firsttextfile = dirf[0]

            for txtfile in dirf:
                ''' load and reshape textfile with gesture data '''
                g = numpy.loadtxt(path + name + "/gesture_" + str(gesturenumber) + "/" + txtfile, delimiter=",")
                g = g.reshape(g.shape[0], 32, g.shape[1] / 32)  # recordingframes
                print name, gesturenumber, "\t\t", g.shape, txtfile
                gn = normalise(g, nn_avg)

                gn = gn.reshape(gn.shape[0], gn.shape[1] * gn.shape[2])

                for i in range(gn.shape[0]):
                    gestures.append(gn[i])
                    targets.append(gesturenumber)

    X_data = numpy.array(gestures)
    X_targets = numpy.array(targets)

    print "X_data", "\t\t", X_data.shape
    print "X_targets", "\t", X_targets.shape

    print X_targets

    return X_data, X_targets, nn_avg

    #===========================================================================
    # ''' normalise data '''
    # nn = normalise(n)
    # gn = normalise(g)
    #
    # gn = gn.reshape(gn.shape[0],gn.shape[1]*gn.shape[2])
    # print gn.shape
    # return
    #
    # ''' create average of 18.5khz frequqncy data '''
    # nn_avg = numpy.mean(nn, axis=1)
    # nn_avg = numpy.mean(nn_avg, axis=0)
    #
    # return nn_avg, gn
    #===========================================================================


def test(nn_avg):
    path = "../../../gestures/Alex/"

    n = numpy.loadtxt(path + "gesture_0/ZimmerLeise2R.txt", delimiter=",")
    n = n.reshape(n.shape[0], 32, n.shape[1] / 32)  # recordingframes
    nn = normalise(n, nn_avg)
    nn = nn.reshape(nn.shape[0], nn.shape[1] * nn.shape[2])

    Y_data = nn[10:]
    Y_targets = numpy.zeros(Y_data.shape[0], dtype=int)

    print "Y_data", "\t\t", Y_data.shape
    print "Y_targets", "\t", Y_targets.shape

    return Y_data, Y_targets



if __name__ == "__main__":

    X_data, X_targets, nn_avg = preprocess()
    c = 10000000
    gamma = 0
    cv = 3
    method = "fit"
    kernel = "poly"
    degree = 3
    coef0 = 1

    Y_data, Y_targets = test(nn_avg)

    train_svm(X_data, X_targets, Y_data, Y_targets, c, gamma, method, cv, degree, coef0, kernel)


   # train_svm(X_train, Y_train, X_test, Y_test)