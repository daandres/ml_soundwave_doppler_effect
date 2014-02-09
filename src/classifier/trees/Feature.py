#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
'''
This class provides functions for feature extraction.
'''
class Feature(object):

    def __init__(self):
        pass
    
    '''
    The function generates a bitorder of shifts in dependence of chronology. For every right shift
    the bitstring is shifted left and combined OR with 1 (append 1). For every left shift the bitstring 
    is shifted left (append 0).
    '''
    def featureOrderOfShifts(self, gesture, shifts):
        
        order_binary = 0

        for shift in shifts:
            if('both' in shift):
                if(shift[0] == 'right'):
                    order_binary = order_binary << 1
                    order_binary = order_binary & 1
                else:
                    order_binary = order_binary << 1
        return order_binary

    '''
    The function identifies concurrent right-left shifts and returns the quantity
    '''
    def featureConcurrentShifts(self, gesture, maxDiff, shiftOrder):
        concurrent_counter = 0
        for shift in shiftOrder:
            if(shift == 'both'):
                concurrent_counter += 1
        return concurrent_counter
            
    '''
    The function computes the distances between sequenced right-left or accordingly
    left-right shifts and between left-left / right-right shifts
    '''
    def shiftDistance(self, gesture, shifts, shift_order):
        distance_contrary = 0
        distance_equal = 0
        
        contrary_list = []
        equal_list = []
        
        if(len(shift_order) > 1):
            prev = 0
            for shift in shifts:
                if(prev != 0):
                    distance = prev[2] - shift[1]
                    distance = 0 if distance <0 else distance
                    if(prev[0] != shift[0]):
                        contrary_list.append(distance)
                    else:
                        equal_list.append(distance)
                prev = shift
            if(len(contrary_list) > 0):
                distance_contrary = sum(contrary_list) / len(contrary_list)
            if(len(equal_list) > 0):
                distance_equal = sum(equal_list) / len(equal_list)
        return distance_contrary, distance_equal
    
    '''
    The function computes the difference of the mean amplitude of right-left shifts
    ''' 
    def featureAmplitudes(self, gesture, shifts):
        ampl_val = 0
        
        right_lefts = []
        prev = 0
        
        for shift in shifts:
            if(prev != 0):
                if(prev[0] == 'right' and shift[0] == 'left'):
                    right_lefts.append((prev,shift))
            prev = shift
        
        ampl_vals = []
        
        for shift_tuple in right_lefts:
            maxAmpl1 = self.getMaxAmplitude(shift_tuple[0][1], shift_tuple[0][2], gesture.amplitudes_right_filtered)
            maxAmpl2 = self.getMaxAmplitude(shift_tuple[1][1], shift_tuple[1][2], gesture.amplitudes_left_filtered)
            diff = abs(maxAmpl1 - maxAmpl2)
            ampl_val = diff 
            ampl_vals.append(ampl_val)
        
        if(len(ampl_vals) > 0):
            return sum(ampl_vals) / len(ampl_vals)
        return 0
        
    '''
    The function calculates the mean max amplitude of a shift
    '''                
    def getMaxAmplitude(self, start, stop, amplitudes):
        ampl_list = []
        for x in amplitudes[start:stop+1]:
            ampl_list.extend(x)   
        return np.mean(ampl_list)       
   
    '''
    The function counts the right and the left shifts
    '''
    def featureCountOfShifts(self, gesture, shifts):
        countOfShiftLeft = 0
        countOfShiftRight = 0
        for shift in shifts:
            if(shift[0] == 'right'):
                countOfShiftRight += 1
            elif(shift[0] == 'left'):
                countOfShiftLeft += 1
        return countOfShiftLeft, countOfShiftRight
  
    