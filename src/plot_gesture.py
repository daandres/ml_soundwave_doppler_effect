'''
Created on 14/12/2013

@author: Benny
'''
import numpy
import pylab
numpy.seterr(all='warn')
import warnings
warnings.simplefilter("error", RuntimeWarning)

x = numpy.arange(40)


def normalise(arr):
    ''' normalise each frame '''
    for d in range(len(arr)):
        for dd in range(len(arr[d])):
            arr[d][dd] = arr[d][dd]/numpy.amax(arr[d][dd])
    return arr

    
def preprocess(gesture):
    name = "Benjamin"
    ''' load and reshape textfile with 20khz frequency data '''
    n = numpy.loadtxt("../gestures/"+name+"/gesture_6/1389637026.txt",delimiter=",")
    n = n.reshape(n.shape[0],32,n.shape[1]/32) #recordingframes
    
    ''' load and reshape textfile with gesture data '''
    g = numpy.loadtxt("../gestures/"+name+"/gesture_"+str(gesture)+"/1389637026.txt",delimiter=",")
    g = g.reshape(g.shape[0],32,g.shape[1]/32) #recordingframes
    
    ''' normalise data '''
    nn = normalise(n)
    gn = normalise(g)
    
    ''' create average of 20khz frequency data '''
    nn_avg = numpy.mean(nn, axis=1)
    nn_avg = numpy.mean(nn_avg, axis=0)
    
    return nn_avg[:,[14, 15,16,17,18,19, 20,21,22,23,24, 25,26,27,28,29, 30,31,32,33,34, 35,36,37,38,39, 40,41,42,43,44, 45,46,47,48,49, 50,51,52,53]], gn[:,:,[14, 15,16,17,18,19, 20,21,22,23,24, 25,26,27,28,29, 30,31,32,33,34, 35,36,37,38,39, 40,41,42,43,44, 45,46,47,48,49, 50,51,52,53]]


def make_plot(arr,avg,length,c):
    ''' plot all recordingFrames '''
    temp = []
    for i in range(length):
        ax = pylab.subplot(5,8,i)
        ax.set_ylim([-0.2,1])
        
        if avg == None:
            pylab.plot(x, arr[i], c) #[::2]
        else:
            arr[i] = (arr[i]-avg)**2
            cond = numpy.where(arr[i] <= 0.025)
            arr[i][cond] = 0
            if numpy.amax(arr[i]) > 0:
                temp.append(arr[i])
            #arr[i] = 0.5*arr[i]/numpy.amax(arr[i])
            pylab.plot(x, arr[i], c)  #[::2]
    return numpy.asarray(temp)
        


def main():
#===============================================================================
#     gesture = 6
#     gestureindex = 4
#     
#     ''' get preprocessed data '''
#     nn_avg, gn = preprocess(gesture)
#     test = numpy.mean(gn[gestureindex], axis=0)
#     print gn.shape, gn[gestureindex].shape, test.shape
#     
#     ''' plot normalised and averaged 20khz frequency data '''
#     pylab.subplot(5,8,39)
#     pylab.plot(x,test,"g")
# 
#     ''' plot normalised gesture data '''
#     length = len(gn[gestureindex])
#     nothing = make_plot(gn[gestureindex],None,length,"b")
#     avggesture = make_plot(gn[gestureindex],nn_avg,length,"r")
#     
#     muh = numpy.zeros(40)
#     for i in avggesture:
#         muh += i
#     muh = muh/numpy.amax(muh)
#     print avggesture.shape, muh.shape
#     ax = pylab.subplot(5,8,37)
#     ax.set_ylim([-0.1,1])
#     pylab.plot(x,muh,"g")
#===============================================================================
    
    g = 5
    for gesture in range(7): #0+g,1+g):
        ''' get preprocessed data '''
        nn_avg, gn = preprocess(gesture)
        
        print "Gesture",gesture
        gesture_avg = []
        for i in range(len(gn)):
            #print i
            temp = []
            for rf in range(len(gn[i])):
                gn[i][rf] = (gn[i][rf]-nn_avg)**2
                cond = numpy.where(gn[i][rf] <= 0.025)
                gn[i][rf][cond] = 0
                if numpy.amax(gn[i][rf]) > 0:
                    temp.append(gn[i][rf])
            
            print len(temp)
            allg = numpy.asarray(temp)
            muh = numpy.zeros(40)
            for t in allg:
                muh += t
            kuh = muh[::2]
            try:
                kuh = kuh/numpy.amax(kuh)
            except RuntimeWarning:
                #print "division error"
                kuh = numpy.zeros(20)
            gesture_avg.append(kuh)
            
            '''
            ax = pylab.subplot(5,8,i)
            ax.set_ylim([-0.1,1])
            scaling = numpy.arange(20)
            pylab.plot(scaling,kuh,"g")
            '''
        average = numpy.mean(numpy.asarray(gesture_avg), axis=0)
        ax = pylab.subplot(2,4,gesture)
        ax.set_ylim([-0.1,1])
        scaling = numpy.arange(20)
        pylab.plot(scaling,average,"g")
        


main()
pylab.show()