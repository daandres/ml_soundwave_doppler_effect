#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sklearn.ensemble import AdaBoostClassifier
from sklearn.cross_validation import cross_val_score
from sklearn import cross_validation
from sklearn.datasets import load_iris
import classifier.trees.ProcessData
from classifier.trees.Feature import Feature
from classifier.trees.GestureModel import GestureModel
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier
import random
import numpy
from MyEstimator import MyEstimator

#gestures = classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_0/1388424714_zimmer_left.txt")
gestures = classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_3/1387647860_zimmer_left.txt")
#gestures = classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_4/1387647860_zimmer_left.txt")
#classifier.trees.ProcessData.plotBoth(gestures)
#classifier.trees.ProcessData.findAmplitude(gestures[2])

#Cases = {}
smoothed = []
cases = []
amplitudes = []
print gestures[0].amplitudes_left_filtered
for i in range(len(gestures)):
    relative = gestures[i].smoothRelative(gestures[i].bins_left_filtered, gestures[i].bins_right_filtered, 2)
    gestures[i].bins_left_filtered, gestures[i].bins_right_filtered = gestures[i].smoothToMostCommonNumberOfBins(relative[0], relative[1], 1)
    print Feature().featureCountOfShifts(gestures[i])
    
    cases.append(Feature().featureOrderOfShifts(gestures[i], 1, []))
    
    Feature().featureAmplitudes(gestures[i])

for case in cases:
    print case

print "right cases: ", 100. / len(cases) * cases.count(0), "%"

print 
print "sklearn.ensemble: "
iris = load_iris()
    
X_train, X_test, y_train, y_test = cross_validation.train_test_split(iris.data, iris.target, test_size=0.4, random_state=0)

myEstimator = MyEstimator()
#clf = AdaBoostClassifier(base_estimator=myEstimator, n_estimators=5, algorithm = 'SAMME')
clf = AdaBoostClassifier(n_estimators=5)
clf.fit(X_train, y_train)
result = clf.predict(X_test) == y_test
rightPredicts = len([x for x in result if x == True])
print 100. / len(result) * rightPredicts 

clf = RandomForestClassifier(n_estimators=3) # Ergebnis schwankt ähnlich bei verschieden Eingaben
clf = clf.fit(X_train, y_train)
result = clf.predict(X_test) == y_test
rightPredicts = len([x for x in result if x == True])
print 100. / len(result) * rightPredicts

clf = GradientBoostingClassifier(n_estimators=100, max_depth=1, random_state=0).fit(X_train, y_train)
result = clf.predict(X_test) == y_test
rightPredicts = len([x for x in result if x == True])
print 100. / len(result) * rightPredicts

clf = ExtraTreesClassifier(max_depth=None, min_samples_split=1, random_state=0)
scores = cross_val_score(clf, iris.data, iris.target)
print scores


myData = []
for x in range(20):
    a = random.randint(0,3)
    b = random.randint(0,3)
    c = random.randint(0,3)
    myData.append([a,b,c])
#print numpy.shape(myData)
myClasses = [random.randint(0,1) for x in range(20)]

clf = RandomForestClassifier(n_estimators=3) # Ergebnis schwankt ähnlich bei verschieden Eingaben
clf = clf.fit(myData[:10], myClasses[:10])
result = clf.predict(myData[10:]) == myClasses[10:]
rightPredicts = len([x for x in result if x == True])
print 100. / len(result) * rightPredicts