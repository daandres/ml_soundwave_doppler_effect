#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scipy.ndimage as ndi
import numpy as np
import math

'''
This class implements different functions to process training data for feature extraction and classification.
'''
class GestureModel(object):

    def __init__(self, data, normalize=True):
        self.data = data
        
        if (normalize):
            self.normalize()
        
        #original bins
        self.bins_left = []
        self.bins_right = []
        #gaussian filtered bins
        self.bins_left_filtered = []
        self.bins_right_filtered = []
        
        #original amplitudes
        self.amplitudes_left = []
        self.amplitudes_right = []
        #gaussian filtered amplitudes
        self.amplitudes_left_filtered = []
        self.amplitudes_right_filtered = []
        
        # iterate over samples and extract num of bins on left/right side of peak larger than 10% of max peak
        for sample in data:
            filtered = ndi.gaussian_filter1d(sample, sigma=1, output=np.float64, mode='nearest')
            peakPosition = len(sample)/2
            peak = sample[peakPosition]
            threshold = peak/10
            
            #left
            pos = peakPosition-1
            numBins = 0
            numBinsFiltered = 0
            amp_left = []
            amp_left_filtered = []
            while pos >= 0:
                #extract bins of original data
                if sample[pos] >= threshold:
                    numBins+=1
                    amp_left.append(sample[pos])
                #extract bins of gaussian filtered data
                if filtered[pos] >= threshold:
                    numBinsFiltered+=1
                    amp_left_filtered.append(filtered[pos])
                pos-=1
            self.bins_left.append(numBins)
            self.bins_left_filtered.append(numBinsFiltered)
            self.amplitudes_left.append(amp_left)
            self.amplitudes_left_filtered.append(amp_left_filtered)
            
            #right
            pos = peakPosition+1
            numBins = 0
            numBinsFiltered = 0
            amp_right = []
            amp_right_filtered = []
            while pos < len(sample):
                #extract bins of original data
                if sample[pos] >= threshold:
                    numBins+=1
                    amp_right.append(sample[pos])
                #extract bins of gaussian filtered data
                if filtered[pos] >= threshold:
                    numBinsFiltered+=1
                    amp_right_filtered.append(filtered[pos])
                pos+=1
            self.bins_right.append(numBins)
            self.bins_right_filtered.append(numBinsFiltered)
            self.amplitudes_right.append(amp_left)
            self.amplitudes_right_filtered.append(amp_left_filtered)
            
        
    

    '''
    Each extracted number of bins on the left and right side is compared with the previous
    smoothed value. If this value is less than minPeakSize the value is replaced with the previous smoothed value.
    This method can be used to remove small variations in the extracted number of bins on both sides.
    '''       
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
    
    
    '''
    Each extracted number of bins on the left and right side is compared with the previous
    value. If this value is less than minPeakSize the value is replaced with the previous value.
    This method can be used to remove small variations in the extracted number of bins on both sides.
    '''       
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
    
    
    '''
    All values of the left and right side are set to the most common number of bins if the absolute 
    difference is smaller than threshold.
    '''
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
    
    '''
    All peaks which are separated by just one step are combined.
    '''
    def combineNearPeaks(self, left_vals, right_vals):
        average_left, average_right = self.mostCommonNumberOfBins()
        
        #left
        combined_left = []
        combined_left.append(left_vals[0])
        for i in range(1, len(left_vals)-1):
            prev = left_vals[i-1]
            current = left_vals[i]
            nxt = left_vals[i+1]
            if prev > average_left and current == average_left and nxt > average_left:
                combined_left.append(math.floor((prev + nxt) / 2))
            else:
                combined_left.append(current)
        combined_left.append(left_vals[-1])
    
        #right
        combined_right = []
        combined_right.append(right_vals[0])
        for i in range(1, len(right_vals)-1):
            prev = right_vals[i-1]
            current = right_vals[i]
            nxt = right_vals[i+1]
            if prev > average_right and current == average_right and nxt > average_right:
                combined_right.append(math.floor((prev + nxt) / 2))
            else:
                combined_right.append(current)
        combined_right.append(right_vals[-1])
        
        return (combined_left, combined_right)
    
    '''
    All samples and all values are normalized to the median peak.
    '''
    def normalize(self):
        #compute median peak value
        median = 0
        for sample in self.data:
            max_value = sample[np.argmax(sample)]
            median += max_value
        median = math.floor(median / len(self.data)) 
        
        #normalize samples
        for sample in self.data:
            diff = median / sample[len(sample)/2]
            for i in range(len(sample)):
                sample[i] = sample[i] * diff
    
    '''          
    This function returns the most common number of bins as tuple (count left, count right), not the median!
    '''
    def mostCommonNumberOfBins(self):
        #left
        counts_left = np.bincount(self.bins_left_filtered)
        #right
        counts_right = np.bincount(self.bins_right_filtered)
        return (np.argmax(counts_left), np.argmax(counts_right))
    
    '''
    The function finds shifts and returns a list of shifts of given direction. A shift is a 
    tuple of the direction (is it a left or right shift?), startSample, stopSample, max bin count 
    '''
    def findShiftsByDirection(self, values, direction):
        commonValue = np.argmax(np.bincount(values))
        found = False
        tempStart = 0
        tempStop = 0
        tempMax = 0
        shifts = []
        for i in range(len(values)):
            value = values[i]
            if(value > commonValue and found == False):
                tempStart = i
                tempMax = value
                found = True
            elif(value > commonValue and found == True):
                if(value > tempMax):
                    tempMax = value
            elif(value <= commonValue and found == True):
                tempStop = i
                shift = (direction, tempStart, tempStop, tempMax)
                shifts.append(shift)
                tempStart, tempStop, tempMax = 0,0,0
                found = False
        return shifts
    
    '''
    The function returns a list of shifts, using function findShiftsByDirection
    '''    
    def findShiftList(self):
        # set shifts
        shifts_left = self.findShiftsByDirection(self.bins_left_filtered, 'left')
        shifts_right = self.findShiftsByDirection(self.bins_right_filtered, 'right')
        shifts = shifts_left + shifts_right
        shifts = sorted(shifts,key=lambda x: x[1])
        return shifts
    
    '''
    Function returns a string list of the chronological order of the shifts. Shifts
    are 'left', 'right' or 'both' (concurrent shift).
    '''
    def findShiftOrder(self, maxDiff, shifts):
        orderList = []
        prev = 0
        
        for i in range(len(shifts)):
            shift = shifts[i]
            if(i > 0):
                if(prev[0] != shift[0]):
                    start_current = shift[1]
                    start_prev = prev[1]
                    diffStart = abs(start_current - start_prev)
                    # concurrent shifts are identified if they start point is lower than
                    # defined maxDiff (2 is a good choice)
                    if(diffStart < maxDiff):
                        orderList.pop()
                        orderList.append('both')

            orderList.append(shift[0])        
            prev = shift
        
        return orderList    
