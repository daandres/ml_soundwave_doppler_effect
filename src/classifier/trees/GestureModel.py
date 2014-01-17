#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    
       
    def smoothRelative(self, left_vals, right_vals, minPeakSize):
        #left
        smoothed_left = []
        smoothed_left.append(left_vals[0])
        for i in range(1, len(left_vals)):
            prev_val = smoothed_left[i-1]
            current_val = left_vals[i]
            diff = abs(current_val - prev_val)
            if diff < minPeakSize:
                smoothed_left.append(prev_val)
            else:
                smoothed_left.append(current_val)
        
        #right
        smoothed_right = []
        smoothed_right.append(right_vals[0])
        for i in range(1, len(right_vals)):
            prev_val = smoothed_right[i-1]
            current_val = right_vals[i]
            diff = abs(current_val - prev_val)
            if diff < minPeakSize:
                smoothed_right.append(prev_val)
            else:
                smoothed_right.append(current_val)
        
        return [smoothed_left, smoothed_right]
    
    
    def smoothAbsolute(self, left_vals, right_vals, minPeakSize):
        average = self.mostCommonNumberOfBins()
        
        #left
        smoothed_left = []
        #erase peaks smaller than minPeakSize
        for value in left_vals:
            diff = abs(value - average[0])
            if diff < minPeakSize:
                smoothed_left.append(average[0])
            else:
                smoothed_left.append(value)
        
        #right
        smoothed_right = []
        #erase peaks smaller than minPeakSize
        for value in right_vals:
            diff = abs(value - average[0])
            if diff < minPeakSize:
                smoothed_right.append(average[0])
            else:
                smoothed_right.append(value)
        
        return [smoothed_left, smoothed_right]
    
    
    def smoothToMostCommonNumberOfBins(self, left_vals, right_vals, threshold):
        average = self.mostCommonNumberOfBins()
        
        #left
        smoothed_left = []
        #erase peaks smaller than minPeakSize
        for value in left_vals:
            diff = abs(value - average[0])
            if diff > threshold:
                smoothed_left.append(value)
            else:
                smoothed_left.append(average[0])
        
        #right
        smoothed_right = []
        #erase peaks smaller than minPeakSize
        for value in right_vals:
            diff = abs(value - average[1])
            if diff > threshold:
                smoothed_right.append(value)
            else:
                smoothed_right.append(average[1])
        
        return [smoothed_left, smoothed_right]
    
    
    #returns the most common number of bins as tuple (count left, count right), not the median!
    def mostCommonNumberOfBins(self):
        #left
        vals_left = []
        for s in self.bins_left_filtered:
            vals_left.append(s)
        counts_left = np.bincount(vals_left)
        
        #right
        vals_right = []
        for s in self.bins_right_filtered:
            vals_right.append(s)
        counts_right = np.bincount(vals_right)
        
        return (np.argmax(counts_left), np.argmax(counts_right))
        
