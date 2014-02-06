'''
Created on 06/02/2014

@author: Benny
'''
import os
import subprocess as sp

class Starter():
    
    def __init__(self):
        
        self.executed = {0: {"program": "notepad", "started": False, "processname": "notepad"},
                         1: {"program": "notepad", "number": 0},
                         2: {"program": "taskmanager", "started": False, "processname": "taskmgr"},
                         3: {"program": "taskmanager", "number": 2},
                         4: {"program": "calculator", "started": False, "processname": "calc"},
                         5: {"program": "calculator", "number": 4}}
        print "Application-Starter loaded"
    
    def startProgramm(self, number):
        self.logic(number)         
    
    def logic(self, number):
        if number != 6:
            if number % 2 == 0:
                if self.executed[number]["started"] == False:
                    self.executed[number]["started"] = self.start(number, self.executed[number]["program"], self.executed[number]["processname"])
                else:
                    self.log("\t"+str(number)+" => "+self.executed[number]["program"]+" already started, only one instance allowed")
            else:
                if self.executed[self.executed[number]["number"]]["started"] != False:
                    self.executed[self.executed[number]["number"]]["started"] = self.terminate(number, self.executed[number]["program"], self.executed[self.executed[number]["number"]]["started"])
                else:
                    self.log("\t"+str(number)+" => "+self.executed[number]["program"]+" not started, nothing to terminate")

             
    
    def start(self, number, program, processname):
        self.log("\t"+str(number)+" => starting "+program)
        proc = sp.Popen(processname)
        return proc.pid
    
    def terminate(self, number, program, processid):
        self.log("\t"+str(number)+" => terminating "+program)
        sp.Popen("TASKKILL /F /PID {pid} /T".format(pid=processid), shell=True, stdout=sp.PIPE)
        return False
    
    def log(self, message):
        print message
