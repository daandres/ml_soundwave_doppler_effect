'''
Created on 14/12/2013

@author: Benny
'''
import numpy
import pylab
import properties.config as config 

x = numpy.arange(64)
gesture = 3

def normalise(arr):
    for d in range(len(arr)):
        for dd in range(len(arr[d])):
            arr[d][dd] = arr[d][dd]/numpy.amax(arr[d][dd])
    return arr

    
def preprocess():
    n = numpy.loadtxt("../gestures/20khz_frequency.txt",delimiter=",")
    n = n.reshape(n.shape[0],config.recordingFrames,n.shape[1]/config.recordingFrames)
    
    g = numpy.loadtxt("../gestures/gesture_2.txt",delimiter=",")
    g = g.reshape(g.shape[0],config.recordingFrames,g.shape[1]/config.recordingFrames)
    
    nn = normalise(n)
    gn = normalise(g)
    
    nn_avg = numpy.mean(nn, axis=1)
    nn_avg = numpy.mean(nn_avg, axis=0)
    
    return nn_avg, gn


def make_plot(arr,avg,length,c):
    for i in range(length):
        ax = pylab.subplot(5,8,i)
        if avg == None:
            pylab.plot(x, arr[i], c)
        else:
            pylab.plot(x, arr[i]-avg, c)
        ax.set_ylim([-0.2,1])


def main():
    nn_avg, gn = preprocess()
    
    pylab.subplot(5,8,39)
    pylab.plot(x,nn_avg,"g")
    
    length = len(gn[gesture])

    make_plot(gn[gesture],None,length,"b")
    make_plot(gn[gesture],nn_avg,length,"r")

main()
pylab.show()