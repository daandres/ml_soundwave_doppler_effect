from classifier.classifier import IClassifier

import numpy as np
import kMeansHelper as kmHelper



class KMeans(IClassifier):
    
    def __init__(self, recorder=None):
        self.name = 'kmeans'
        self.currentRecordFrame = None
        
        self.recorder = recorder
        #bob
        self.kmH = kmHelper.kMeansHepler()
        self.kmeans = None
        self.checkOnline = False
        self.startBuffern = False
        
        #new
        
        self.percentRatio = 0.0
        self.gestureIdx = 0
        self.gestureArray = []
        #bob end
 
    def getName(self):
        return self.name

 
    def startTraining(self, args=[]):
        from view.ui_kmeans_visualizer import ViewUIKMeans
        self.viewUiKmeans_ = ViewUIKMeans(self, self.getName)
        self.viewUiKmeans_.startNewThread()
        self.recorder.classifyStart(self)
  

 
    def classify(self, data):

        if self.startBuffern:  
            self.bufferArray = np.roll(self.bufferArray, -1, axis=0)
            self.bufferArray[15] = self.kmH.normalizeSignalLevelSecond(data)
            if self.checkOnline:
                result = self.kmH.reduceDimensionality(self.bufferArray)
                #print 'result : \n', self.bufferArray[0] 
                if result is not None:
                        #print result.shape
                        result = np.asarray(result)
                        result = result.reshape(result.shape[0]*result.shape[1])
                        #result = np.asarray(result)
                
                if len(result) == self.kmeans.cluster_centers_.shape[1]:
                    #print result, ' , '
                    self.kMeansOnline(result)
                else:
                    print 'len(result) : ', len(result)
        
 
    def startValidation(self):
        pass

 
    def load(self, filename=""):
        pass

 
    def save(self, filename=""):
        pass

 
    def loadData(self, filename=""):
        pass

 
    def saveData(self, filename=""):
        pass

 
    def printClassifier(self):
        pass

    #bob
    def fillBuffer(self, bufferSize, callback):
        self.idx = 0
        self.progress = 0.0
        self.bufferSize = bufferSize
        #self.bufferArray = np.zeros((self.bufferSize, self.idxRight -self.idxLeft))
        self.bufferArray = np.zeros((self.bufferSize, 64))
        self.startBuffern = True
        self.callback = callback
        print 'fillBuffer'
        print self.bufferArray.shape
        
    def getBuffer(self):
        return self.bufferArray
    # changed scope
    def setKMeans(self, kMeans):
        self.kmeans = kMeans
        self.gestureArray = np.array(['bob\n', 'bob\n', 'bob\n', 'bob\n', 'bob\n', 'bob\n', 'bob\n', 'bob\n', 'bob\n', 'bob\n'])
        
        
        
    def kMeansOnline(self, checkArray):
        class_  = self.kmeans.transform(checkArray)
        cluster =  self.kmH.checkClusterDistance(class_, self.percentRatio)
        self.setGestureArray(cluster)
       
        if cluster == -1:
            print '-1'
        elif cluster == 0:
            print '    0'
        elif cluster == 1:
            print '        1'
        elif cluster == 2:
            print '            2'
        elif cluster == 3:
            print '                3'
        elif cluster == 4:
            print '                    4'
        elif cluster == 5:
            print '                        5'
        elif cluster == 6:
            print '                            6'
        elif cluster == 7:
            print '                                7'                                                
        
    def setGestureArray(self, cluster):
        self.gestureIdx = self.gestureIdx+1 
        class_ = "-"
        if cluster == -1:
            class_ = '\t-1\n'
        elif cluster == 0:
            class_ = '\t\t0\n'
        elif cluster == 1:
            class_ = '\t\t\t1\n'
        elif cluster == 2:
            class_ = '\t\t\t\t2\n'
        elif cluster == 3:
            class_ = '\t\t\t\t\t3\n'
        elif cluster == 4:
            class_ = '\t\t\t\t\t\t4\n'
        elif cluster == 5:
            class_ = '\t\t\t\t\t\t\t5\n'
        elif cluster == 6:
            class_ = '\t\t\t\t\t\t\t\t6\n'
        elif cluster == 7:
            class_ = '\t\t\t\t\t\t\t\t7\n'
   
        
        self.gestureArray[self.gestureIdx] = class_
        self.gestureIdx = (self.gestureIdx+1)%9                                           
    
    
    def getGestureArray(self):
        return np.asarray(self.gestureArray)
    
        
    def checkKMeansOnline(self):
        self.checkOnline = not self.checkOnline
    #new
    def setPercentRatio(self, pRatio):
        self.percentRatio = pRatio    
    #bob end
