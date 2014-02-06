__author__ = 'Manuel Dudda'

import svm as svm
import properties.config as c

svmConfig = c.getInstance('../../').getConfig("svm")

svm = svm.SVM(None, svmConfig)
svm.startTraining()
svm.show_confusion_matrix()