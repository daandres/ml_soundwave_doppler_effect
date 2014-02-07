#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sklearn.ensemble import AdaBoostClassifier
from sklearn.cross_validation import cross_val_score
from sklearn import cross_validation
import classifier.trees.ProcessData
from classifier.trees.Feature import Feature
from classifier.trees.GestureModel import GestureModel
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier
#from sklearn.ensemble import BaggingClassifier
import numpy


#gestures = classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_0/1388424714_zimmer_left.txt")

#gestures = classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_1/1387647578_zimmer_left.txt")

#gestures = classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_2/1387660041_fernsehen.txt")
#gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_3/1387647860_zimmer_left.txt")
#gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_4/1387647860_zimmer_left.txt")
#gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_6/gesture_6_zimmer_1.txt")
print "start read in"
gestures = classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_2/1391437451.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_2/1391437809.txt")
#gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_2/1391615397.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_3/1391439011.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_3/1391439281.txt")
#gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_3/1391615558.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_4/1391439536.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_4/1391439659.txt")
#gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_4/139161589.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_0/1391435081.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_0/1391435669.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_1/1391436572.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_1/1391436738.txt")
#gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Annalena/gesture_1/1391615026.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_6/gesture_6_zimmer_1.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_6/gesture_6_zimmer_3.txt")
#gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_6/gesture_6_zimmer_3.txt")

print "read in"

#for i in range(150,200):
counter = 0
for i in range(len(gestures)):
    featureVector = []
    relative = gestures[i].smoothRelative(gestures[i].bins_left_filtered, gestures[i].bins_right_filtered, 2)
    smoothed = gestures[i].smoothToMostCommonNumberOfBins(relative[0], relative[1], 1)
    gestures[i].bins_left_filtered, gestures[i].bins_right_filtered = gestures[i].combineNearPeaks(smoothed[0], smoothed[1])
    shifts_left, shifts_right = Feature().featureCountOfShifts(gestures[i])
    featureVector.append(shifts_left + shifts_right)
    featureVector.append(shifts_left)
    featureVector.append(shifts_right)
    
    featureVector.append(Feature().featureOrderOfShifts(gestures[i]))
    featureVector.append(Feature().featureConcurrentShifts(gestures[i], 2))
    featureVector.append(Feature().featureAmplitudes(gestures[i]))
    
    distance_contrary, distance_equal = Feature().shiftDistance(gestures[i])
    featureVector.append(distance_contrary)
    featureVector.append(distance_equal)

    
    gestures[i].featureVector = featureVector
    #print featureVector
    #if( featureVector[3] == 0):
    #    counter += 1

#print 100. / len(gestures) * counter
    
    
    
data = []
data2 = []
for gesture in gestures:
    data.append(gesture.featureVector)
    #l = []
    #l.extend(gesture.bins_left_filtered)
    #l.extend(gesture.bins_right_filtered)
    #l.extend(gesture.featureVector)
    #data2.append(l)

targets = []
for class_ in [2,2,3,3,4,4,0,0,1,1,6,6]:
    for frameIndex in range(50):
        targets.append(class_)

print "targets"
#X_train, X_test, y_train, y_test = cross_validation.train_test_split(data2, targets, test_size=0.4, random_state=0)
X_train, X_test, y_train, y_test = cross_validation.train_test_split(data, targets, test_size=0.4, random_state=0)

#for i in range(1,100):
    
    #for learning in range(1,10):
        #for depth in range(1,4):
                    
            #esitmator, learning rate, depth, result
            #clf = GradientBoostingClassifier(n_estimators=i, max_depth=depth, learning_rate=learning/10.).fit(X_train, y_train)
            #result = clf.predict(X_test) == y_test
            #rightPredicts = len([x for x in result if x == True])
            #print i, ",", learning/10., ",", depth, ",", 100. / len(result) * rightPredicts

            
        #clf = AdaBoostClassifier(n_estimators=i, learning_rate = learning/10.)
        #clf.fit(X_train, y_train)
        #result = clf.predict(X_test) == y_test
        #rightPredicts = len([x for x in result if x == True])
        #print i, ",", learning/10., ",", 100. / len(result) * rightPredicts
#for crit in ["gini", "entropy"]:
#    for i in range(1,100):
#        clf = RandomForestClassifier(n_estimators=i, criterion= crit)
#        clf.fit(X_train, y_train)
#        result = clf.predict(X_test) == y_test
#        rightPredicts = len([x for x in result if x == True])
#        print crit, ",", i, ",", 100. / len(result) * rightPredicts
for i in range(23,24):
    clf = GradientBoostingClassifier(n_estimators=i, learning_rate = 0.2, max_depth = 2)
    clf.fit(X_train, y_train)
    result = clf.predict(X_test) == y_test
    rightPredicts = len([x for x in result if x == True])
    print i, ",", 100. / len(result) * rightPredicts
