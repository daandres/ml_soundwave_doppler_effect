'''
Created on 14/12/2013

@author: Benny
'''
from scipy.ndimage import gaussian_filter1d
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
        
def smoothListGaussian(list,strippedXs=False,degree=6):  
    window=degree*2-1  
    weight=numpy.array([1.0]*window)  
    weightGauss=[]  
    
    for i in range(window):  
        i=i-degree+1  
        frac=i/float(window)  
        gauss=1/(numpy.exp((4*(frac))**2))  
        weightGauss.append(gauss)  

    weight=numpy.array(weightGauss)*weight
    smoothed=[0.0]*(len(list)-window)
    
    for i in range(len(smoothed)):  
        smoothed[i]=sum(numpy.array(list[i:i+window])*weight)/sum(weight)  
    
    print list.shape, len(smoothed)
    return smoothed

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
    for gesture in range(0,1): #0+g,1+g):
        ''' get preprocessed data '''
        nn_avg, gn = preprocess(gesture)
        
        print "Gesture",gesture
        gesture_avg = []
        for i in range(0,len(gn)):
            #i = 5
            temp = []
            for rf in range(len(gn[i])):
                gn[i][rf] = gn[i][rf]-nn_avg
                cond = numpy.where(gn[i][rf] <= 0.1)
                gn[i][rf][cond] = 0
                
                #if gn[i][rf].sum(axis=0) > 5:
                #    print "no good frame"
                
                if numpy.amax(gn[i][rf]) > 0:
                    temp.append(gn[i][rf])
            
            while len(temp) < 16:
                temp.append(numpy.zeros(40))
            #print len(temp)
            
            even = temp[:16:2] 
            odd = temp[1:16:2]
            
            test = numpy.asarray(list(numpy.asarray(even) + numpy.asarray(odd)))/2.0

            for rf in range(0,len(test)):
                #print numpy.amax(test[rf])
                try:
                    d = 1#numpy.amax(test[rf])
                    p = gaussian_filter1d(test[rf]/d, 1.5)
                    #p = p/numpy.amax(p)
                except:
                    p = test[rf]

                
                ax = pylab.subplot(2,4,rf)
                ax.set_ylim([-0.1,1])
                scaling = numpy.arange(40)
                if rf == 0:
                    pylab.plot(scaling,p,"b")
                else:
                    pylab.plot(scaling,p,"g")
            
            '''return
            for rf in range(0,len(temp[:16]),2):
                ax = pylab.subplot(4,4,rf)
                ax.set_ylim([-0.1,1])
                scaling = numpy.arange(40)
                pylab.plot(scaling,(temp[rf]+temp[rf+1])/2.0,"g")
            
            return
            '''    
            '''
            print i,"=>",len(temp),
            if len(temp) > 8:
                offset = (len(temp) - 8)/2
                g = numpy.asarray(temp[offset:offset+8])
                for dd in range(len(g)):
                    g[dd] = g[dd]/numpy.amax(g[dd])
                    
            elif len(temp) == 8:
                g = numpy.asarray(temp)
                for dd in range(len(g)):
                    g[dd] = g[dd]/numpy.amax(g[dd])
            elif len(temp) < 8:
                print "\t not enough relevant recordingframes",
            print ""
            
            trainingset = g.reshape(320,)[::2]
            print trainingset.shape
            
            ax = pylab.subplot(1,1,0)
            ax.set_ylim([-0.1,1])
            scaling = numpy.arange(160)
            pylab.plot(scaling,trainingset,"g")
            
            '''    
            
            ''' 
            muh = gn[i].sum(axis=0)     
            kuh = muh
            try:
                kuh = kuh/numpy.amax(kuh)
            except RuntimeWarning:
                kuh = numpy.zeros(40)
            gesture_avg.append(kuh)
            
            ax = pylab.subplot(5,8,i)
            ax.set_ylim([-0.1,1])
            scaling = numpy.arange(40)
            pylab.plot(scaling,kuh,"g")
            '''
        
        #=======================================================================
        # average = numpy.mean(numpy.asarray(gesture_avg), axis=0)
        # ax = pylab.subplot(2,4,gesture)
        # ax.set_ylim([-0.1,1])
        # scaling = numpy.arange(20)
        # pylab.plot(scaling,average,"g")
        #=======================================================================
        


main()
pylab.show()