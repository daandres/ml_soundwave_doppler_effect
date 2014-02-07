'''
Created on 07/02/2014

@author: Benny
'''

'''general imports '''
import os
import numpy as np

''' explicit imports '''
from scipy.ndimage import gaussian_filter1d


class Preprocesser():
    
    def __init__(self):
        
        print "Preprocesser loaded"
        

    @staticmethod
    def normalise_framesets(framesets, ref_frequency_frame):
        ''' normalise framesets and substract ref_frequencyframe '''
        for frameset_nr in range(len(framesets)):
            for frame_nr in range(len(framesets[frameset_nr])):
                current_frameset = framesets[frameset_nr][frame_nr]
                framesets[frameset_nr][frame_nr] = (current_frameset / np.amax(current_frameset)) - ref_frequency_frame
        return framesets
    
    
    def preprocess_frame(self, frame_data, ref_frequency_frame):
        try:
            ''' normalise and slice dataframe '''
            normalized_data_with_ref_frequency = frame_data / np.amax(frame_data)
            normalized_data = normalized_data_with_ref_frequency - ref_frequency_frame
            
            ''' set small noisy data to 0 '''
            frame = normalized_data
            irrelevant_samples = np.where(frame <= self.threshold)
            frame[irrelevant_samples] = 0.0
        except:
            frame = np.zeros(self.wanted_frames)
        return frame
    
    
    def preprocess_frames(self, frames, ref_frequency_frame, framerange, new_preprocess):
        if self.new_preprocess:
            ''' get all recordingframes which contain relevant gesture information '''
            # current_frameset = [self.preprocess_frame(frame, self.ref_frequency_frame) for frame in frames if np.amax(self.preprocess_frame(frame, self.ref_frequency_frame)) > 0]
            # list comprehension is maybe to difficult and probably slower because of two preprocessing-steps, so to keep it nice and simple a for-loop is used #
            current_frameset = []
            for frame in frames:
                current_frameset = []
                processed_frame = self.preprocess_frame(frame, self.ref_frequency_frame)
                if np.amax(processed_frame) > 0:
                    current_frameset.append(processed_frame)
                    
            ''' if less than 16, append frames with zeros '''
            while len(current_frameset) < self.framerange/2:
                current_frameset.append(np.zeros(self.wanted_frames))
            
            ''' slice the first 16 recordingframes to two lists (even/odd) and compute the average of each pair '''
            relevant_frames = np.asarray(list(np.asarray(current_frameset[:self.framerange/2:2] ) + np.asarray(current_frameset[1:self.framerange/2:2])))/2.0
            
            ''' smooth each frame and apply NO normalization either before or after smoothing '''
            for frame in range(len(relevant_frames)):
                try:
                    divisor = 1 #np.amax(relevant_frames[frame])
                    relevant_frames[frame] = gaussian_filter1d(relevant_frames[frame]/divisor, 1.5)
                except:
                    relevant_frames[frame] = gaussian_filter1d(relevant_frames[frame], 1.5)
                    
            ''' reshape to 1d-array '''   
            processed_frames = relevant_frames.reshape(self.wanted_frames*self.framerange/4,)
            
        else:
            ''' preprocess all frames '''
            # current_frameset = [self.preprocess_frame(frame, self.ref_frequency_frame) for frame in frames]
            # list comprehension is maybe easier and faster to read, but to keep it consistent a for-loop is used as in the if-branch #
            current_frameset = []
            for frame in frames:
                current_frameset.append(self.preprocess_frame(frame, self.ref_frequency_frame))
                    
            ''' sum up all wanted frames to one gestureframe '''
            gesture_frame = np.asarray(current_frameset).sum(axis=0)

            ''' normalise summed gesture frame '''
            try:
                processed_frames = gesture_frame / np.amax(gesture_frame)
            except RuntimeWarning:
                processed_frames = np.zeros(gesture_frame.shape[0])
        return processed_frames
    
    
    def slice_frame(self, frame, slice_left, slice_right, samples_per_frame):
        ''' slice one single 1d-frame from 64 to 40 datavalues '''
        return frame[self.slice_left:(self.samples_per_frame - self.slice_right)]
    
    
    def slice_framesets(self, framesets, slice_left, slice_right, samples_per_frame):
        ''' slice 3d-framesets from 64 to 40 datavalues '''
        return framesets[:, :, self.slice_left:(self.samples_per_frame - self.slice_right)]

    
    def load_gesture_framesets(self, txt_file, samples_per_frame):
        ''' load gesture training datasets ''' 
        gesture_plain = np.loadtxt(txt_file, delimiter=",")
        num_framesets = gesture_plain.shape[0]
        num_samples_total = gesture_plain.shape[1]
        num_frames_per_frameset = num_samples_total / self.samples_per_frame
        gesture_framesets_plain = gesture_plain.reshape(num_framesets, num_frames_per_frameset, self.samples_per_frame)
        return gesture_framesets_plain

    
    def load_ref_frequency_frame(self, gestures_path, slice_left, slice_right, samples_per_frame):
        ref_frequency_txt_file = os.path.join(self.gestures_path, 'Benjamin', 'gesture_6', '1389637026.txt')

        ''' load and reshape referencefrequency data with 18500Hz '''
        ref_frequency_framesets_plain = self.load_gesture_framesets(ref_frequency_txt_file, samples_per_frame)
        ref_frequency_framesets = self.normalise_framesets(ref_frequency_framesets_plain, 0)
        
        ''' reduce to one single average referencefrequency frame and slice to 40 datavalues '''
        ref_frequency_avg_frameset = np.mean(ref_frequency_framesets, axis=1)
        ref_frequency_frame = self.slice_frame(np.mean(ref_frequency_avg_frameset, axis=0), slice_left, slice_right, samples_per_frame)
        return ref_frequency_frame
