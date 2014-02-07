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
    def featureOrderOfShifts(self, gesture):
        
        order_binary = 0

        gesture.shifts_left = self.findShifts(gesture.bins_left_filtered, 'left')
        gesture.shifts_right = self.findShifts(gesture.bins_right_filtered, 'right')
        shifts = gesture.shifts_left + gesture.shifts_right
        shifts = sorted(shifts,key=lambda x: x[1])
                        
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
    def featureConcurrentShifts(self, gesture, maxDiff):
        
        concurrent_counter = 0
        orderList = []

        gesture.shifts_left = self.findShifts(gesture.bins_left_filtered, 'left')
        gesture.shifts_right = self.findShifts(gesture.bins_right_filtered, 'right')
        shifts = gesture.shifts_left + gesture.shifts_right
        shifts = sorted(shifts,key=lambda x: x[1])
        
        prev = 0
        
        for i in range(len(shifts)):
            shift = shifts[i]
            if(i > 0):
                if(prev[0] != shift[0]):
                    start_current = shift[1]
                    start_prev = prev[1]
                    diffStart = abs(start_current - start_prev)
                    if(diffStart < maxDiff):
                        orderList.pop()
                        orderList.append('both')
                        concurrent_counter += 1

            orderList.append(shift[0])        
            prev = shift
                
        
        gesture.shift_order = orderList
        return concurrent_counter    
    
    '''
    The function computes the distances between sequenced right-left or accordingly
    left-right shifts and between left-left / right-right shifts
    '''
    def shiftDistance(self, gesture):
        shift_order = gesture.shift_order
        distance_contrary = 0
        distance_equal = 0
        
        contrary_list = []
        equal_list = []
        
        shifts_left = gesture.shifts_left
        shifts_right = gesture.shifts_right
        shifts = shifts_left + shifts_right
        shifts = sorted(shifts,key=lambda x: x[1])
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
    def featureAmplitudes(self, gesture):
        ampl_val = 0
        
        shifts = gesture.shifts_left + gesture.shifts_right
        shifts = sorted(shifts,key=lambda x: x[1])
        
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
            ampl_val = diff / 100.
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
    def featureCountOfShifts(self, gesture):
        countOfShiftLeft = len(self.findShifts(gesture.bins_left_filtered, 'left'))
        countOfShiftRight = len(self.findShifts(gesture.bins_right_filtered, 'right'))
        return countOfShiftLeft, countOfShiftRight
  
    # Verschiebung ist charakterisiert durch Anfang, Ende, maximale Binanzahl 
    # und ob sie links oder rechts des Peaks ist        
    '''
    The function finds shifts and returns a list of shifts. A shift is a tuple of the direction
    (is it a left or right shift?), startSample, stopSample, max bin count 
    '''
    def findShifts(self, values, direction):
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
    
    
    