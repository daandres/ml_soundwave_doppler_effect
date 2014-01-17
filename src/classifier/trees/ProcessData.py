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
    for gesture in gestures:
        plt.figure(0)
        plt.plot(gesture.bins_left_filtered, color='red')
        plt.plot(gesture.bins_right_filtered, color='blue')
        plt.axis([0,32,0,32])
        
        #relative_smoothed = gesture.smoothRelative(gesture.bins_left_filtered, gesture.bins_right_filtered, 2)
        relative_smoothed = gesture.smoothAbsolute(gesture.bins_left_filtered, gesture.bins_right_filtered, 2)
        #smoothed = gesture.smoothToMostCommonNumberOfBins(relative_smoothed[0], relative_smoothed[1], 1)
        plt.figure(1)
        plt.plot(relative_smoothed[0], color='magenta')
        plt.plot(relative_smoothed[1], color='cyan')
        plt.axis([0,32,0,32])

        plt.show()
        
def findAmplitude(gesture):
    print gesture.bins_left
    print gesture.bins_right
    amplitudes_left = []
    amplitudes_right = []
    plotTestData([gesture])
    mean_left = np.mean(gesture.bins_left)
    mean_right = np.mean(gesture.bins_right)
    temp =[]
    for i in range(len(gesture.bins_right)):
        current = gesture.bins_right[i]
        if(current > mean_right):
            temp.append(current)
        else:
            if(temp != []):
                if(len(temp) > 2):
                    print "Amplitude rechts gefunden"
                    temp = []
    
    for i in range(len(gesture.bins_left)):
        current = gesture.bins_left[i]
        if(current > mean_left):
            temp.append(current)
        else:
            if(temp != []):
                if(len(temp) > 2):
                    print "Amplitude links gefunden"
                    temp = []
            
