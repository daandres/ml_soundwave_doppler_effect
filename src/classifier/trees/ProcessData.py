#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from classifier.trees.GestureModel import GestureModel

def readData(filename):
    fid = open(filename,"r")
    data = []
    lines = []
    for line in fid.readlines():
        lines.append(line.strip())
    for line in lines:
        data.append([float(x) for x in line.split(",")])
    fid.close()
    return data



def getTestData(filename):
    gestures = []
    data = readData(filename)
    for line in data:
        if (len(line) == 2048):
            tmp = np.reshape(line, (32,64))
            gestures.append(GestureModel(tmp))
    return gestures

def plotTestData(gestures): 
    for gesture in gestures:
        plt.plot(gesture.bins_left, color='red')
        plt.plot(gesture.bins_right)
        plt.axis([0,32,0,32])
        plt.show()

def plotFilteredTestData(gestures): 
    for gesture in gestures:
        plt.plot(gesture.bins_left_filtered, color='red')
        plt.plot(gesture.bins_right_filtered)
        plt.axis([0,32,0,32])
        plt.show()

def plotBoth(gestures):
    index = 0
    for gesture in gestures:
        print "current index: ", index
        #absolute_smoothed = gesture.smoothAbsolute(gesture.bins_left_filtered, gesture.bins_right_filtered, 2)
        relative_smoothed = gesture.smoothRelative(gesture.bins_left_filtered, gesture.bins_right_filtered, 2)
        smoothed = gesture.smoothToMostCommonNumberOfBins(relative_smoothed[0], relative_smoothed[1], 1)
        plt.figure(0)
        plt.plot(smoothed[0], color='red')
        plt.plot(smoothed[1], color='blue')
        plt.axis([0,32,0,32])
        
        combined_smoothed = gesture.combineNearPeaks(smoothed[0], smoothed[1])
        plt.figure(1)
        plt.plot(combined_smoothed[0], color='magenta')
        plt.plot(combined_smoothed[1], color='cyan')
        plt.axis([0,32,0,32])

        plt.show()
        index += 1
        
