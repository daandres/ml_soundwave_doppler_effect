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
        plt.axis([0,32,0,20])
        plt.show()

