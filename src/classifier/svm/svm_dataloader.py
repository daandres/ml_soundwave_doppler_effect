'''
Created on 07/02/2014

@author: Benny
'''

'''general imports '''
import os
import numpy as np
import pandas as pd

''' explicit imports '''
from svm_preprocessor import Preprocessor


class Dataloader():
    
    def __init__(self):
        self.preprocessor = Preprocessor()
    
    
    def load_framesets(self, textfile, samples_per_frame):
        frames_plain = np.asarray(pd.read_csv(textfile, sep=',', header=None))
        #frames_plain = np.loadtxt(textfile, delimiter=",")
        num_framesets = frames_plain.shape[0]
        num_samples_total = frames_plain.shape[1]
        num_frames_per_frameset = num_samples_total / samples_per_frame
        framesets = frames_plain.reshape(num_framesets, num_frames_per_frameset, samples_per_frame)
        return framesets
    
        
    def load_gesture_framesets(self, nClasses, subdirs, gestures_path, slice_left, slice_right, samples_per_frame, ref_frequency_frame, framerange, new_preprocess, threshold, wanted_frames):
        gestures = []
        targets = []
        for gesture_nr in range(nClasses):
            print "load gesture", gesture_nr
            for subdir in subdirs:
                files = [c for a,b,c in os.walk(os.path.join(gestures_path, subdir, 'gesture_' + str(gesture_nr)))][0]
                for textfile in files:
                    ''' load and reshape textfile with gesture data '''
                    text_file_with_path = os.path.join(gestures_path, subdir, 'gesture_' + str(gesture_nr), textfile)
                    gesture_framesets_plain = self.load_framesets(text_file_with_path, samples_per_frame)
                    gesture_framesets = self.preprocessor.slice_framesets(gesture_framesets_plain, slice_left, slice_right, samples_per_frame)
                    
                    ''' create one gesture frame from relevant frames '''
                    for frameset_nr in range(gesture_framesets.shape[0]):
                        ''' start preprocessing of frameset '''
                        normalised_gesture_frame = self.preprocessor.preprocess_frames(gesture_framesets[frameset_nr], ref_frequency_frame, framerange, new_preprocess, threshold, wanted_frames)
                        
                        ''' append gestureframe and targetclass to their corresponding arrays '''
                        gestures.append(normalised_gesture_frame)
                        targets.append(gesture_nr)
        
        ''' convert to numpy array '''
        data = np.array(gestures)
        targets = np.array(targets)
        print data.shape, targets.shape
        #return train_test_split(data, targets, random_state=0)
        return data, targets

    
    def load_ref_frequency_frame(self, gestures_path, slice_left, slice_right, samples_per_frame):
        ''' load referencefrequency data with 18500Hz '''
        ref_frequency_txt_file = os.path.join(gestures_path, 'Benjamin', 'gesture_6', '1389637026.txt')
        ref_frequency_framesets_plain = self.load_framesets(ref_frequency_txt_file, samples_per_frame)
        
        ''' normalse referencefrequency datadarames '''
        ref_frequency_framesets = self.preprocessor.normalise_framesets(ref_frequency_framesets_plain, 0)
        
        ''' reduce to one single average referencefrequency frame and slice to 40 datavalues '''
        ref_frequency_avg_frameset = np.mean(ref_frequency_framesets, axis=1)
        ref_frequency_frame = self.preprocessor.slice_frame(np.mean(ref_frequency_avg_frameset, axis=0), slice_left, slice_right, samples_per_frame)
        print ref_frequency_frame
        return ref_frequency_frame
