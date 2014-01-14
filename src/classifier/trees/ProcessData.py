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

#data = readData("../../../gestures/Annalena/gesture_3/1389686429_10x.txt")
#data = readData("../../../gestures/Benjamin/gesture_1/1389637026.txt")
data = readData("../../../gestures/Daniel/gesture_3/1387647860_zimmer_left.txt")
#data = readData("../../../gestures/Annalena/gesture_3/1388337880_hintergrundgespraech_50x.txt")

gestures = []
for line in data:
    if (len(line) == 2048):
        tmp = np.reshape(line, (32,64))
        gestures.append(GestureModel(tmp))

import matplotlib.pyplot as plt
for gesture in gestures:
    plt.plot(gesture.bins_left, color='red')
    plt.plot(gesture.bins_right)
    plt.axis([0,32,0,32])
    plt.show()
