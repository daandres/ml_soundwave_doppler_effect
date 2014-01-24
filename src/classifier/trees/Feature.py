#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
class Feature(object):

    def __init__(self):
        pass
    
    #reihenfolge der frequenzverschiebungen
    def featureOrderOfShifts(self, gesture, maxDiff):
        cases = {}
        cases[0] = [['right', 'left'], ['right']]
        cases[1] = [['right','left','right','left'], ['right','left','right']]
        cases[2] = [['both', 'both'], ['both']]
        
        shifts_left = self.findShifts(gesture.bins_left_filtered, 'left')
        shifts_right = self.findShifts(gesture.bins_right_filtered, 'right')
        gesture.shifts_left = shifts_left
        gesture.shifts_right = shifts_right
        shifts = shifts_left + shifts_right
        shifts = sorted(shifts,key=lambda x: x[1])
        prev = 0
        orderList = []
        for i in range(len(shifts)):
            shift = shifts[i]
            if(i > 0):
                if(prev[0] != shift[0]):
                    start_current = shift[1]
                    start_prev = prev[1]
                    stop_current = shift[2]
                    stop_prev = prev[2]
                    diffStart = abs(start_current - start_prev)
                    intersection = abs(max(start_current,start_prev) - min(stop_current,stop_prev))
                    union = abs(min(start_current,start_prev) - max(stop_current,stop_prev))
                    #print "intersection", intersection
                    #print "union", union
                    #print "ffffffffff", union - intersection
                    coverage = union - intersection
                    if(diffStart < maxDiff or coverage <= 2):
                        orderList.pop()
                        orderList.append('both')
                    else:
                        orderList.append(shift[0])
                        prev = shift
                else:
                    orderList.append(shift[0])
                    prev = shift
                        
            else:
                orderList.append(shift[0])        
                prev = shifts[i]
        #Cases = self.findShiftCases(orderList, 0, Cases)
        #return Cases
        gesture.shift_order = orderList
        for k,v in cases.iteritems():
            if(orderList in v):
                return k  
        return -1 
        #print "no case available", orderList
        # Herausfinden, welche Kombinationen auch noch oft vorkommen pro case oder rauswerfen?
           
    def featureAmplitudes(self, gesture):
        ampl_val = 0
        shift_order = gesture.shift_order
        if(len(shift_order) > 1):
            if(len(shift_order) == 2):
                if(shift_order[0] == 'right' and shift_order[1] == 'left'):
                    # start, stop 
                    maxAmpl1 = self.getMaxAmplitude(gesture.shifts_right[0][1], gesture.shifts_right[0][2], gesture.amplitudes_right_filtered)
                    maxAmpl2 = self.getMaxAmplitude(gesture.shifts_left[0][1], gesture.shifts_left[0][2], gesture.amplitudes_left_filtered)
                    diff = abs(maxAmpl1 - maxAmpl2)
                    ampl_val = diff / 100.
            if(len(shift_order) == 3):
                if(shift_order[0] == 'right' and shift_order[1] == 'left' and shift_order[2] == 'right'):   
                    maxAmpl1 = self.getMaxAmplitude(gesture.shifts_right[0][1], gesture.shifts_right[0][2], gesture.amplitudes_right_filtered)
                    maxAmpl2 = self.getMaxAmplitude(gesture.shifts_left[0][1], gesture.shifts_left[0][2], gesture.amplitudes_left_filtered)
                    diff = abs(maxAmpl1 - maxAmpl2)
                    ampl_val = diff / 100.
            if(len(shift_order) == 4):
                if(shift_order[0] == 'right' and shift_order[1] == 'left' and shift_order[2] == 'right' and shift_order[3] == 'left'):   
                    maxAmpl1 = self.getMaxAmplitude(gesture.shifts_right[0][1], gesture.shifts_right[0][2], gesture.amplitudes_right_filtered)
                    maxAmpl2 = self.getMaxAmplitude(gesture.shifts_left[0][1], gesture.shifts_left[0][2], gesture.amplitudes_left_filtered)
                    
                    maxAmpl3 = self.getMaxAmplitude(gesture.shifts_right[1][1], gesture.shifts_right[1][2], gesture.amplitudes_right_filtered)
                    maxAmpl4 = self.getMaxAmplitude(gesture.shifts_left[1][1], gesture.shifts_left[1][2], gesture.amplitudes_left_filtered)
                    
                    diff1 = abs(maxAmpl1 - maxAmpl2)
                    diff2 = abs(maxAmpl3 - maxAmpl4)
                    ampl_val = ((diff1+diff2)/2) / 100.
        return ampl_val
                    
                    
    def getMaxAmplitude(self, start, stop, amplitudes):
        ampl_list = []
        for x in amplitudes[start:stop+1]:
            ampl_list.extend(x)   
        return np.mean(ampl_list)       
   
    #anzahl verschiebungen
    def featureCountOfShifts(self, gesture):
        countOfShiftLeft = len(self.findShifts(gesture.bins_left_filtered, 'left'))
        countOfShiftRight = len(self.findShifts(gesture.bins_right_filtered, 'right'))
        return countOfShiftRight, countOfShiftLeft
  
    def findShiftCases(self, orderList, dataClass, Cases):
        #cases = {}
   
        Cases[','.join(orderList)] = Cases.get(','.join(orderList), 0) + 1
        return Cases
  
    # Verschiebung ist charakterisiert durch Anfang, Ende, maximale Binanzahl 
    # und ob sie links oder rechts des Peaks ist        
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
                tempMax = values[i]
                found = True
            elif(value > commonValue and found == True):
                if(value > tempMax):
                    tempMax = values[i]
            elif(value <= commonValue and found == True):
                tempStop = i
                shift = (direction, tempStart, tempStop, tempMax)
                shifts.append(shift)
                tempStart, tempStop, tempMax = 0,0,0
                found = False
        return shifts
    
    
    