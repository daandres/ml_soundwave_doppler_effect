'''
Created on 13.01.2014

@author: mutz
'''
import scipy.ndimage as ndi
import numpy as np
import math

class GestureModel(object):

    def __init__(self, data):
        self.data = data
        self.bins_left = []
        self.bins_right = []
        self.bins_left_filtered = []
        self.bins_right_filtered = []
        # iterate over samples and extract num of bins on left/right side of peak
        for sample in data:
            filtered = ndi.gaussian_filter1d(sample, sigma=1, output=np.float64, mode='nearest')
            peakPosition = len(sample)/2
            peak = sample[peakPosition]
            threshold = peak/10
            #left
            pos = peakPosition-1
            numBins = 0
            numBinsFiltered = 0
            while pos >= 0:
                if sample[pos] >= threshold:
                    numBins+=1
                if filtered[pos] >= threshold:
                    numBinsFiltered+=1
                pos-=1
            self.bins_left.append(numBins)
            self.bins_left_filtered.append(numBinsFiltered)
            #right
            pos = peakPosition+1
            numBins = 0
            numBinsFiltered = 0
            while pos < len(sample):
                if sample[pos] >= threshold:
                    numBins+=1
                if filtered[pos] >= threshold:
                    numBinsFiltered+=1
                pos+=1
            self.bins_right.append(numBins)
            self.bins_right_filtered.append(numBinsFiltered)
    
    def smoothFilteredPeaks(self):
        #left
        for i in range(len(self.bins_left_filtered)-2):
            current_val = self.bins_left_filtered[i]
            next_val = self.bins_left_filtered[i+1]
            next_next_val = self.bins_left_filtered[i+2]
            if current_val == next_next_val and math.pow(current_val - next_val, 2) == 1:
                self.bins_left_filtered[i+1] = current_val
        #right
        for i in range(len(self.bins_right_filtered)-2):
            current_val = self.bins_right_filtered[i]
            next_val = self.bins_right_filtered[i+1]
            next_next_val = self.bins_right_filtered[i+2]
            if current_val == next_next_val and math.pow(current_val - next_val, 2) == 1:
                self.bins_right_filtered[i+1] = current_val
          
          
    #returns the most common number of bins as tuple (count left, count right), not the median!
    def mostCommonNumberOfBins(self):
        #left
        vals_left = []
        for s in self.bins_left_filtered:
            vals_left.append(s)
        counts_left = np.bincount(vals_left)
        
        #right
        vals_right = []
        for s in self.bins_left_filtered:
            vals_right.append(s)
        counts_right = np.bincount(vals_right)
        
        return (np.argmax(counts_left), np.argmax(counts_right))
        
    #reihenfolge der frequenzverschiebungen
    def featureOrderOfShifts(self):
        pass
    
    #verschiebungsrichtungen
    def featureDirectionsOfShifts(self):
        pass
    
    #anzahl verschiebungen
    def featureCountOfShifts(self):
        pass
    
    
    