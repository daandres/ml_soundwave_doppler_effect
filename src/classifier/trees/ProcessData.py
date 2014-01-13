import numpy as np
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

data = readData("../../../gestures/Annalena/gesture_1/1389608527_10x.txt")

gestures = []
for line in data:
    if (len(line) == 2048):
        try:
            gestures.append(GestureModel(np.reshape(line, (32,64))))
        except IndexError as detail:
            print 'Error:', detail

import matplotlib.pyplot as plt
for gesture in gestures:
    plt.plot(gesture.bins_left, color='red')
    plt.plot(gesture.bins_right)
    plt.axis([0,32,0,20])
    plt.show()
