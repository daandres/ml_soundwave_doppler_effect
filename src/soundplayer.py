import pyaudio
# # To use wavebender checkout this repo: https://github.com/zacharydenton/wavebender.git and install it with python setup.py
import wavebender as wb
from myStream import MyStream
class Sound:
    
    def __init__(self):
        self.audioDev = pyaudio.PyAudio()
        self.audioStream = None
        self.play = True
    
    def startPlaying(self, frequency=440.0, amplitude=0.5, framerate=48100, duration=30):
        # create stream
        channels = ((wb.sine_wave(frequency, amplitude=amplitude, framerate=framerate),),)
               
        while True:
            try:
                samples = wb.compute_samples(channels, framerate * duration * 1)
                self.audioStream = MyStream(self.audioDev.open(format=self.audioDev.get_format_from_width(2), channels=1, rate=framerate, output=True))
                wb.write_wavefile(self.audioStream, samples)
            except AttributeError:
                pass
            if self.play == False:
                self.audioStream.stopIt()
                self.audioDev.terminate()
                break

    def stopPlaying(self):
        self.play = False

if __name__ == '__main__':
    s = Sound()
    s.startPlaying(21000.0, framerate=48100, duration=30)
    s.stopPlaying()

