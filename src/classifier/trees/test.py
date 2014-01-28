#!/usr/bin/env python
# -*- coding: utf-8 -*-

# http://www.hdm-stuttgart.de/~maucher/Python/ComputerVision/html/Filtering.html
import classifier.trees.ProcessData
from classifier.trees.GestureModel import GestureModel
import scipy.ndimage as ndi
import matplotlib.pyplot as plt
import numpy as np

def testFilter():
    ones = np.ones(64)
    ones[31] = 2
    ones[32] = 4
    ones[33] = 2
    modes = ['reflect', 'constant', 'nearest', 'mirror', 'wrap']
    for mode in modes:
        filtered = ndi.gaussian_filter1d(ones, sigma=1, output=np.float64, mode=mode)
        plt.plot(ones, color='red', marker=".")
        plt.plot(filtered, marker=".")
        plt.axis([0,64,0,5])
        plt.show()

def showDiffFilteredNoFiltered(filename):
    gestures = classifier.trees.ProcessData.getTestData(filename)
    classifier.trees.ProcessData.plotBoth(gestures)


def showSamplesOfFirstGesture(filename, index):
    #read data and split samples
    data = classifier.trees.ProcessData.readData(filename)
    gestures = []
    for line in data:
        if (len(line) == 2048):
            tmp = np.reshape(line, (32,64))
            gestures.append(GestureModel(tmp))

    #show samples of gesture at index             
    gesture = gestures[index]
    for data in gesture.data:
        max_pos = data[np.argmax(data)]
        threshold_line = []
        for i in range(len(data)):
            threshold_line.append(max_pos/10)
            
        filtered = ndi.gaussian_filter1d(data, sigma=1, output=np.float64, mode='nearest')
        
        plt.plot(data, color='red', marker=".")
        plt.plot(filtered, marker=".")
        plt.plot(threshold_line, color = 'black')
        plt.axis([0,64,0,1000])
        plt.show()
    
    return
    for g in gesture:
        threshold_line = []
        max_pos = g[np.argmax(g)]
        for i in range(len(g)):
            threshold_line.append(max_pos/10)
        
        filtered = ndi.gaussian_filter1d(g, sigma=1, output=np.float64, mode='nearest')
        plt.plot(g, color='red', marker=".")
        plt.plot(filtered, marker=".")
        plt.plot(threshold_line, color = 'black')
        plt.axis([0,64,0,1000])
        plt.show()


#testFilter()

#filename = "../../../gestures/Daniel/gesture_0/1388424714_zimmer_left.txt" #Right-To-Left-One-Hand
#filename = "../../../gestures/Daniel/gesture_1/1387647578_zimmer_left.txt" #Top-to-Bottom-One-Hand
#filename = "../../../gestures/Daniel/gesture_2/1387660041_fernsehen.txt" #Entgegengesetzt with two hands
#filename = "../../../gestures/Daniel/gesture_3/1387647860_zimmer_left.txt" #Single-push with one hand
filename = "../../../gestures/Daniel/gesture_4/1387647860_zimmer_left.txt" #Double-push with one hand
#filename = "../../../gestures/Benjamin/gesture_4/1389637026.txt" #Right-To-Left-One-Hand

#showDiffFilteredNoFiltered(filename)
showSamplesOfFirstGesture(filename, 3)
