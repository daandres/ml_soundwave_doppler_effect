'''
Created on 13.01.2014

@author: mutz
'''

class GestureModel(object):

    def __init__(self, data):
        self.data = data
        self.bins_left = []
        self.bins_right = []
        # iterate over samples and extract num of bins on left/right side of peak
        for sample in data:
            peakPosition = len(sample)/2
            peak = sample[peakPosition]
            threshold = peak/10
            #left
            pos = peakPosition-1
            numBins = 0
            while pos >= 0:
                if sample[pos] >= threshold:
                    numBins+=1
                pos-=1
            self.bins_left.append(numBins)
            #right
            pos = peakPosition+1
            numBins = 0
            while pos < len(sample):
                if sample[pos] >= threshold:
                    numBins+=1
                pos+=1
            self.bins_right.append(numBins)
