'''
Created on 13.01.2014

@author: mutz
'''
import scipy.ndimage as ndi
import numpy as np

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
    
