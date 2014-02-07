from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import config.config as c
import util.util as u
import util.dataUtil as d
import util.hmmUtil as h
import util.gmmUtil as g

import numpy as np
from sklearn.hmm import GMMHMM
from sklearn.mixture import GMM

PRE_DATA = "Preproc-Data"
RAW_DATA = "Raw-Data"
GMM_DATA = "GMM-Samples"
GMM_T_DATA = "Trained GestureGMM-Samples"

KEY_PREFIX = "alt+"
GESTURE_PREF = "gesture "

class Plot():
    
    def __init__(self, gesture=0, index=0, gmms = {}):
        self.gesture = gesture
        self.dp = d.DataUtil()
        self.mu = h.HMM_Util()
        self.gmms = gmms
        self.surf = None
        self.name = PRE_DATA
        self.index = index
        self.dClass = 1
        self.data = u.loadData(gesture)
        self.actionPoint = []
        self.X = []
        self.Y = []
        self.Z = []

    def onclick(self, event):
        ''' handling click event '''
        if event.button == 3:
            if self.dClass == 0:
                self.name = PRE_DATA
                self.actionPoint=[]
                self.plotPreprocData()
                self.dClass += 1
            elif self.dClass == 1:
                self.name = RAW_DATA
                self.actionPoint=[]
                self.plotRaw()
                self.dClass += 1
            elif self.dClass == 2:
                self.name = GMM_DATA
                self.actionPoint=[]
                self.plotGestureGmms()
                self.dClass = 3
            elif self.dClass == 3:
                self.name = GMM_T_DATA
                self.actionPoint=[]
                self.plotTrainedGestureGmms()
                self.dClass = 0
                
    def onpress(self, event):
        ''' handling key-press event '''
        # matplotlib bug
        if event.key != None:
            key = event.key.replace(KEY_PREFIX, "")
            
            if key.isdigit():
                gesture = int(key)
                if 0 <= gesture <= 7:
                    self.index = 0
                    self.dClass = 1
                    self.gesture = gesture
                    self.plotPreprocData()
            if key == 'down':
                self.index -= 1
            if key == 'up':
                self.index += 1
            if self.index < 0:
                self.index = len(self.data)-1
            elif self.index >= len(self.data):
                self.index = 0
            self.plot()
        
    def onscroll(self, event):
        ''' handling scroll event '''
        if event.button == "down":
            self.index -= 1
        elif event.button == "up":
            self.index += 1
        
        if self.index < 0:
            self.index = len(self.data)-1
        elif self.index >= len(self.data):
            self.index = 0
        self.plot()
        #print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(event.button, event.x, event.y, event.xdata, event.ydata)

    def setData(self, data):
        self.data = data

    def initAxis(self):
        ''' inits X and Y Axis depending on loaded data (Z) '''
        self.X, self.Y, self.Z = [],[],[]
        _, x, y = np.shape(self.data)
        for i in range(x):
            # Y: time
            self.Y.append(range(0, y))
            # X: frequency
            self.X.append([i]*y) 
        self.Z = self.data[0]

    def initPlot(self):
        ''' init figure, surface and plot '''
        self.fig = plt.figure()
        self.initAxis()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.surf = self.ax.plot_surface(self.X, self.Y, self.Z, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)
        self.ax.set_zlim(-0.03, 1.03)
        self.ax.set_title(GESTURE_PREF + str(self.gesture) + ", " +self.name + ": " + str(self.index+1))
        self.ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
        self.fig.colorbar(self.surf, shrink=0.5, aspect=5)
        self.fig.canvas.mpl_connect('scroll_event', self.onscroll)
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('key_press_event', self.onpress)

    def show(self):
        ''' show plot '''
        plt.show()

    def plot(self):
        ''' plot new data set '''
        self.ax.cla()
        self.fig.clf()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.surf = self.ax.plot_surface(self.X, self.Y, self.data[self.index], rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)
        self.ax.set_title(GESTURE_PREF + str(self.gesture) + ", " +self.name + ": " + str(self.index+1))
        if len(self.actionPoint) > 0:
            self.ax.scatter(self.actionPoint[self.index],0,0,'0', c='r')
        self.ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
        self.fig.canvas.draw()

    def plotPreprocData(self):
        ''' plot preprocessed data '''
        self.data = u.loadData(self.gesture)
        self.index = 0
        self.initAxis()
        self.plot()

    def plotRaw(self):
        ''' plot raw data '''
        self.data = u.loadRaw(self.gesture)
        
        self.actionPoint = []
        for d in self.data:
            self.actionPoint.append(self.dp._getHighestSum(d))
        self.index = 0
        self.initAxis()
        self.plot()

    def setGMMs(self, gmms):
        ''' set gmms to sample 
            {gestureName: [gmm, gmm, ...]}
        '''
        self.gmms = gmms

    def plotGestureGmms(self):
        ''' plot gmm-sample data '''
        mg = g.GMM_Util()
        gmms = mg.sample(self.gesture)
        data = []
        for i in range(13):
            lis = []
            for gmm in gmms:
                sample = gmm.sample(25)
                sample = np.mean(sample, 0)
                lis.append(np.ravel(sample))
            data.append(lis)
        self.data = data
        self.index = 0
        self.initAxis()
        self.plot()

    def plotTrainedGestureGmms(self):
        ''' plot gmm-sample data '''
        if self.gesture in self.gmms.keys():
            self.name = GMM_T_DATA
            gmms = self.gmms[self.gesture] 
        else:
            print "no trained gmm found"
            self.name = GMM_DATA
            mg = g.GMM_Util()
            gmms = mg.sample(self.gesture)
        data = []
        for i in range(13):
            lis = []
            for gmm in gmms:
                sample = gmm.sample(50)
                sample = np.mean(sample, 0)
                lis.append(np.ravel(sample))
            data.append(lis)
        self.data = data
        self.index = 0
        self.initAxis()
        self.plot()
