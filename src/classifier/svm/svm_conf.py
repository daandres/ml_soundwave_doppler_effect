__author__ = 'Manuel Dudda'

import svm as svm
import properties.config as c

self.gestures_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'gestures')

svmConfig = c.getInstance().getConfig("svm")

svm = svm.SVM()
svm.startTraining()
svm.show_confusion_matrix()