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
gestures = classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_2/1387660041_fernsehen.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_3/1387647860_zimmer_left.txt")
gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_4/1387647860_zimmer_left.txt")

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
    gestures[i].featureVector = featureVector
    
data = []
for gesture in gestures:
    data.append(gesture.featureVector)

targets = []
for class_ in [2,3,4]:
    for frameIndex in range(50):
        targets.append(class_)

X_train, X_test, y_train, y_test = cross_validation.train_test_split(data, targets, test_size=0.4, random_state=0)

clf = AdaBoostClassifier(n_estimators=5)
clf.fit(X_train, y_train)
result = clf.predict(X_test) == y_test
rightPredicts = len([x for x in result if x == True])
print 100. / len(result) * rightPredicts