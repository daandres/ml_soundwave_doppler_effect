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
import numpy


#gestures = classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_0/1388424714_zimmer_left.txt")

#gestures = classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_1/1387647578_zimmer_left.txt")
gestures = classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_2/1387660041_fernsehen.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_3/1387647860_zimmer_left.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_4/1387647860_zimmer_left.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_6/gesture_6_zimmer_1.txt")


for i in range(len(gestures)):
    featureVector = []
    relative = gestures[i].smoothRelative(gestures[i].bins_left_filtered, gestures[i].bins_right_filtered, 2)
    gestures[i].bins_left_filtered, gestures[i].bins_right_filtered = gestures[i].smoothToMostCommonNumberOfBins(relative[0], relative[1], 1)
    shifts_left, shifts_right = Feature().featureCountOfShifts(gestures[i])
    featureVector.append(shifts_left + shifts_right)
    featureVector.append(shifts_left)
    featureVector.append(shifts_right)
    
    featureVector.append(Feature().featureOrderOfShifts(gestures[i], 2))
    featureVector.append(Feature().featureAmplitudes(gestures[i]))
    
    distance_contrary, distance_equal = Feature().shiftDistance(gestures[i])
    featureVector.append(distance_contrary)
    featureVector.append(distance_equal)

    
    gestures[i].featureVector = featureVector
    print featureVector
    
    
data = []
data2 = []
for gesture in gestures:
    data.append(gesture.featureVector)
    l = []
    l.extend(gesture.bins_left_filtered)
    l.extend(gesture.bins_right_filtered)
    data2.append(l)

targets = []
for class_ in [2,3,4,6]:
    for frameIndex in range(50):
        targets.append(class_)

#X_train, X_test, y_train, y_test = cross_validation.train_test_split(data2, targets, test_size=0.4, random_state=0)
X_train, X_test, y_train, y_test = cross_validation.train_test_split(data, targets, test_size=0.4, random_state=0)

for i in range(1,100):
    #clf = AdaBoostClassifier(n_estimators=i)
    #clf.fit(X_train, y_train)
    #result = clf.predict(X_test) == y_test
    #rightPredicts = len([x for x in result if x == True])
    #print i, 100. / len(result) * rightPredicts
    
    clf = GradientBoostingClassifier(n_estimators=i, max_depth=2, random_state=0).fit(X_train, y_train)
    result = clf.predict(X_test) == y_test
    rightPredicts = len([x for x in result if x == True])
    print i, 100. / len(result) * rightPredicts
print clf.predict([0, 0, 0, -1, 0, 0, 0])
