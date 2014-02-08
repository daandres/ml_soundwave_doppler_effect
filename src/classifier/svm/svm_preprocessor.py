'''
Created on 07/02/2014

@author: Benny
'''

'''general imports '''
import numpy as np

''' explicit imports '''
from scipy.ndimage import gaussian_filter1d


class Preprocessor():

    @staticmethod
    def normalise_framesets(framesets, ref_frequency_frame):
        ''' normalise framesets and substract ref_frequencyframe '''
        for frameset_nr in range(len(framesets)):
            for frame_nr in range(len(framesets[frameset_nr])):
                current_frameset = framesets[frameset_nr][frame_nr]
                framesets[frameset_nr][frame_nr] = (current_frameset / np.amax(current_frameset)) - ref_frequency_frame
        return framesets
    
    
    def preprocess_frame(self, frame_data, ref_frequency_frame, threshold, wanted_frames):
        try:
            ''' normalise and slice dataframe '''
            normalized_data_with_ref_frequency = frame_data / np.amax(frame_data)
            normalized_data = normalized_data_with_ref_frequency - ref_frequency_frame
            
            #print np.amax(normalized_data)
            ''' set small noisy data to 0 '''
            frame = normalized_data
            irrelevant_samples = np.where(frame <= threshold)
            frame[irrelevant_samples] = 0.0
        except:
            frame = np.zeros(wanted_frames)
        return frame
    
    
    def preprocess_frames(self, frames, ref_frequency_frame, framerange, new_preprocess, threshold, wanted_frames):
        if new_preprocess:
            ''' get all recordingframes which contain relevant gesture information '''
            # current_frameset = [self.preprocess_frame(frame, self.ref_frequency_frame) for frame in frames if np.amax(self.preprocess_frame(frame, self.ref_frequency_frame)) > 0]
            # list comprehension is maybe to difficult and probably slower because of two preprocessing-steps, so to keep it nice and simple a for-loop is used #
            current_frameset = []
            for frame in frames:
                current_frameset = []
                processed_frame = self.preprocess_frame(frame, ref_frequency_frame, threshold, wanted_frames)
                if np.amax(processed_frame) > 0:
                    current_frameset.append(processed_frame)
                    
            ''' if less than 16, append frames with zeros '''
            while len(current_frameset) < framerange/2:
                current_frameset.append(np.zeros(wanted_frames))
            
            ''' slice the first 16 recordingframes to two lists (even/odd) and compute the average of each pair '''
            relevant_frames = np.asarray(list(np.asarray(current_frameset[:framerange/2:2] ) + np.asarray(current_frameset[1:framerange/2:2])))/2.0
            
            #===================================================================
            # ''' smooth each frame and apply NO normalization either before or after smoothing '''
            # for frame in range(len(relevant_frames)):
            #     try:
            #         divisor = 1 #np.amax(relevant_frames[frame])
            #         relevant_frames[frame] = gaussian_filter1d(relevant_frames[frame]/divisor, 1.5)
            #     except:
            #         relevant_frames[frame] = gaussian_filter1d(relevant_frames[frame], 1.5)
            #===================================================================
                    
            ''' reshape to 1d-array '''   
            processed_frames = relevant_frames.reshape(wanted_frames*framerange/4,)
            #print np.amax(processed_frames)
            
        else:
            ''' preprocess all frames '''
            # current_frameset = [self.preprocess_frame(frame, self.ref_frequency_frame) for frame in frames]
            # list comprehension is maybe easier and faster to read, but to keep it consistent a for-loop is used as in the if-branch #
            current_frameset = []
            for frame in frames:
                current_frameset.append(self.preprocess_frame(frame, ref_frequency_frame))
                    
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
        return frame[slice_left:(samples_per_frame - slice_right)]
    
    
    def slice_framesets(self, framesets, slice_left, slice_right, samples_per_frame):
        ''' slice 3d-framesets from 64 to 40 datavalues '''
        return framesets[:, :, slice_left:(samples_per_frame - slice_right)]
