#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from classifier.trees.GestureModel import GestureModel

'''
Read all lines of the file into a list
'''
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

'''
Creates a list with gestures. Each gesture contains 32 samples with 64 values (amplitudes).
'''
def getTestData(filename):
    gestures = []
    data = readData(filename)
    for line in data:
        if (len(line) == 2048):
            tmp = np.reshape(line, (32,64))
            gestures.append(GestureModel(tmp))
    return gestures

#TODO: das könnt man auch ohne funktion im direkt im code machen oder? :) 
def makeGesture(dataArray):
    gesture = GestureModel(dataArray)
    return gesture

'''
Show graph with the number of extracted bins of the original signal
on the left (red) and right (blue) side of max amplitude.
'''
def plotTestData(gestures): 
    for gesture in gestures:
        plt.plot(gesture.bins_left, color='red')
        plt.plot(gesture.bins_right)
        plt.axis([0,32,0,32])
        plt.show()

'''
Show graph with the number of extracted bins of the smoothed signal
on the left (red) and right (blue) side of max amplitude.
'''
def plotFilteredTestData(gestures): 
    for gesture in gestures:
        plt.plot(gesture.bins_left_filtered, color='red')
        plt.plot(gesture.bins_right_filtered)
        plt.axis([0,32,0,32])
        plt.show()

'''
Show two graphs to compare the smoothed number of peaks with the original number of peaks.
'''
#TODO: rename function
def plotBoth(gestures):
    index = 0
    for gesture in gestures:
        print "current line: ", index
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
        
