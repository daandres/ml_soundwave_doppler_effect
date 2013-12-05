import pyaudio
# # To use wavebender checkout this repo: https://github.com/zacharydenton/wavebender.git and install it with python setup.py
import wavebender as wb

class Sound:
    
    def __init__(self):
        self.audioDev = pyaudio.PyAudio()
        self.audioStream = None
    
    def startPlaying(self, frequency=440.0, amplitude=0.5, framerate=48100, duration=30):
        # create stream
        self.audioStream = self.audioDev.open(format=self.audioDev.get_format_from_width(2), 
                                              channels=1, rate=framerate, output=True)
        channels = ((wb.sine_wave(frequency, amplitude=amplitude, framerate=framerate),),)
        samples = wb.compute_samples(channels, framerate * duration * 1)
        wb.write_wavefile(self.audioStream, samples)
        
    
    def stopPlaying(self):
        self.audioStream.stop_stream()
        self.audioStream.close()
        self.audioDev.terminate()   

if __name__ == '__main__':
    s = Sound()
    s.startPlaying(21000.0, framerate=48100, duration=30)
    s.stopPlaying()

