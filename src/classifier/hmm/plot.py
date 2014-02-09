from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import config.config as c
import util.dataUtil as d
import util.hmmUtil as h
import util.gmmUtil as g

import numpy as np

PRE_DATA = "Preproc-Data"
RAW_DATA = "Raw-Data"
GMM_T_DATA = "GestureGMM-Samples"


KEY_PREFIX = "alt+"
GESTURE_PREF = "Gesture "

class Plot():
    
    ''' Class for plotting raw, preproc and gmm sample data
    right click:        change data mode
    mouse wheel:        change data index
    0-7:                change gesture
     '''
    
    def __init__(self, gesture=0, index=0, gmms = {}):
        self.gesture = gesture
        self.du = d.DataUtil()
        self.mu = h.HMM_Util()
        self.gmms = gmms
        self.surf = None
        self.name = RAW_DATA
        self.index = index
        self.dClass = 1
        self.X = []
        self.Y = []
        self.Z = []

    def onclick(self, event):
        ''' handling click event '''
        if event.button == 3:
            if self.dClass == 0:
                self.name = RAW_DATA
                self.actionPoint=[]
                self.plotRaw()
                self.dClass += 1
            elif self.dClass == 1:
                self.name = PRE_DATA
                self.actionPoint=[]
                self.plotPreprocData()
                self.dClass += 1
            elif self.dClass == 2:
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
                    self.plotRaw()
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
        self.data = self.du.loadRaw3dGesture(self.gesture)
        self.initAxis()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.surf = self.ax.plot_surface(self.X, self.Y, self.data[self.index], rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)
        self._setTitle()
        self.ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
        self.fig.canvas.mpl_connect('scroll_event', self.onscroll)
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('key_press_event', self.onpress)
        
        plt.show()

    def _setTitle(self):
        self.ax.set_title(GESTURE_PREF + str(self.gesture) + ", " +self.name + ": " + str(self.index+1))


    def plot(self):
        ''' plot new data set '''
        self.ax.cla()
        self.fig.clf()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.surf = self.ax.plot_surface(self.X, self.Y, self.data[self.index], rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)
        self._setTitle()
        self.ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
        self.fig.canvas.draw()

    def plotPreprocData(self):
        ''' plot preprocessed data '''
        self.data = self.du.loadData(self.gesture)
        self.index = 0
        self.initAxis()
        self.plot()

    def plotRaw(self):
        ''' plot raw data '''
        try:
            self.data = self.du.loadRaw3dGesture(self.gesture)
        except Exception:
            return
        self.index = 0
        self.initAxis()
        self.plot()

    def setGMMs(self, gmms):
        ''' set gmms to sample 
            {gestureName: [gmm, gmm, ...]}
        '''
        self.gmms = gmms

    def plotTrainedGestureGmms(self):
        ''' plot gmm-sample data '''
        
        self.name = GMM_T_DATA
        if self.gesture in self.gmms.keys():
            gmms = self.gmms[self.gesture] 
        else:
            print "no trained gmm found"
            mg = g.GMM_Util()
            data = self.du.loadData(self.gesture)
            gmms = mg.sample(data)
        data = []
        for i in range(c.framesTotal):
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
