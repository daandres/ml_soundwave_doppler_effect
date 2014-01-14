from sklearn.ensemble import AdaBoostClassifier
from sklearn.cross_validation import cross_val_score
import classifier.trees.ProcessData
from classifier.trees.GestureModel import GestureModel



targets = [0,3]

gestures = classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_0/1388424714_zimmer_left.txt")
#gestures += classifier.trees.ProcessData.getTestData("../../../gestures/Daniel/gesture_0/1388424714_zimmer_left.txt")
#classifier.trees.ProcessData.plotTestData(gestures)
#clf = AdaBoostClassifier(n_estimators=100)
#scores = cross_val_score(clf, iris.data, iris.target)