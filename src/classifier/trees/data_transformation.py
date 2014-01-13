import numpy as np


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
# 10 Gesten hintereinander
#data = readData("../../../gestures/Annalena/gesture_0/1389607062_10x.txt")
data = readData("../../../gestures/Annalena/gesture_1/1389608527_10x.txt")

# einzelne Gesten
#data = readData("../../../gestures/Annalena/gesture_0/1389094277.txt")
#data = readData("../../../gestures/Annalena/gesture_0/1389540552.txt")
#data = readData("../../../gestures/Annalena/gesture_0/1389552847.txt")

# 50 Gesten hintereinander
#data = readData("../../../gestures/Annalena/gesture_0/1388337419_hintergrundgespraech_50x.txt")
#data = readData("../../../gestures/Daniel/gesture_0/1388424714_zimmer_left.txt")

# data_ ist ein 3-dim Array mit allen Daten
data_ = []
for line in data:
    data_.append(np.reshape(line, (32,64)))
    
#print np.shape(data_)

# Speichere Peaks
max_vals = np.zeros((np.shape(data_)[0],32))

for row_index in range(len(data_)):
    for frame_index in range(len(data_[row_index])):
        for item_index in range(len(data_[row_index][frame_index])):
            if(data_[row_index][frame_index][item_index] > max_vals[row_index][frame_index]):
                max_vals[row_index][frame_index] = data_[row_index][frame_index][item_index]

# Berechne prozentualen Schwellenwert
min_vals = np.zeros(np.shape(max_vals))
for row_index in range(len(max_vals)):
    for item_index in range(len(max_vals[row_index])):
        min_vals[row_index][item_index] = max_vals[row_index][item_index]/100 * 20  # 20% des Peaks
print np.shape(min_vals)

# Zähle Bins links und rechts des Peaks
bins_left = np.zeros((np.shape(data_)[0],32))
bins_right = np.zeros((np.shape(data_)[0],32))
for row_index in range(len(data_)):
    for frame_index in range(len(data_[row_index])):
        frame_bins_left = []
        frame_bins_right = []
        for item_index in range(len(data_[row_index][frame_index])):
            if(data_[row_index][frame_index][item_index] >= min_vals[row_index][frame_index]):
                if(item_index < len(data_[row_index][frame_index])/2):
                    frame_bins_left.append(data_[row_index][frame_index][item_index])
                    
                elif(item_index > len(data_[row_index][frame_index])/2):
                    frame_bins_right.append(data_[row_index][frame_index][item_index])
    
        bins_left[row_index][frame_index] = len(frame_bins_left)
        bins_right[row_index][frame_index] = len(frame_bins_right)

import matplotlib.pyplot as plt
# Plot: linke Bins rot, rechte Bins blau, jeweils ein Bild pro Geste, x-Achse: Abtastpunkte, y-Achse: Bins
for row_index in range(len(bins_left)):
    plt.plot(bins_left[row_index], color='red')
    plt.plot(bins_right[row_index])
    plt.axis([0,32,0,20])
    plt.show()
