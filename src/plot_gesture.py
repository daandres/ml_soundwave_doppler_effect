'''
Created on 14/12/2013

@author: Benny
'''
import numpy
import pylab
import properties.config as config 

x = numpy.arange(64)
gesture = 1

def normalise(arr):
    ''' normalise each frame '''
    for d in range(len(arr)):
        for dd in range(len(arr[d])):
            arr[d][dd] = arr[d][dd]/numpy.amax(arr[d][dd])
    return arr

    
def preprocess():
    ''' load and reshape textfile with 20khz frequency data '''
    n = numpy.loadtxt("../gestures/Benjamin/185000hz.txt",delimiter=",")
    n = n.reshape(n.shape[0],32,n.shape[1]/32) #recordingframes
    
    ''' load and reshape textfile with gesture data '''
    g = numpy.loadtxt("../gestures/Benjamin/gesture_0/1389637026.txt",delimiter=",")
    g = g.reshape(g.shape[0],32,g.shape[1]/32) #recordingframes
    
    ''' normalise data '''
    nn = normalise(n)
    gn = normalise(g)
    
    ''' create average of 20khz frequqncy data '''
    nn_avg = numpy.mean(nn, axis=1)
    nn_avg = numpy.mean(nn_avg, axis=0)
    
    return nn_avg, gn


def make_plot(arr,avg,length,c):
    ''' plot all recordingFrames '''
    for i in range(length):
        ax = pylab.subplot(5,8,i)
        if avg == None:
            pylab.plot(x, arr[i], c)
        else:
            pylab.plot(x, arr[i]-avg, c)
        ax.set_ylim([-0.2,1])


def main():
    ''' get preprocessed data '''
    nn_avg, gn = preprocess()
    
    ''' plot normalised and averaged 20khz frequency data '''
    pylab.subplot(5,8,39)
    pylab.plot(x,nn_avg,"g")
    
    ''' plot normalised gesture data '''
    length = len(gn[gesture])
    make_plot(gn[gesture],None,length,"b")
    make_plot(gn[gesture],nn_avg,length,"r")

main()
pylab.show()