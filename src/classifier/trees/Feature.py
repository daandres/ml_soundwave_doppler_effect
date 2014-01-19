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
        
        shifts_left = self.findShifts(gesture[0], 'left')
        shifts_right = self.findShifts(gesture[1], 'right')
        shifts = shifts_left + shifts_right
        shifts = sorted(shifts,key=lambda x: x[1])
        prev = 0
        orderList = []
        for i in range(len(shifts)):
            shift = shifts[i]
            if(i > 0):
                if(prev[0] != shift[0]):
                    diffStart = shift[1] - prev[1]
                    diffStop = shift[2] - prev[2]
                    if(diffStart < maxDiff and diffStop < maxDiff):
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
        for k,v in cases.iteritems():
            if(orderList in v):
                return k
            
        return "no case available", orderList
        # Herausfinden, welche Kombinationen auch noch oft vorkommen pro case oder rauswerfen?
           
            
   
    #anzahl verschiebungen
    def featureCountOfShifts(self, gesture):
        countOfShiftLeft = len(self.findShifts(gesture[0], 'left'))
        countOfShiftRight = len(self.findShifts(gesture[1], 'right'))
        return (countOfShiftRight, countOfShiftLeft)
  
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
    
    
    