import pyaudio
# # To use wavebender checkout this repo: https://github.com/zacharydenton/wavebender.git and install it with python setup.py
import wavebender as wb
from myStream import MyStream
# import winsound

class Sound:

    def __init__(self):
        self.audioDev = pyaudio.PyAudio()
        self.audioStream = None
        self.play = True

    #===========================================================================
    # def startPlaying(self, frequency, amplitude, framerate, duration):
    #     while True:
    #         try:
    #             winsound.Beep(int(frequency),duration*1000)
    #         except AttributeError:
    #             pass
    #         if self.play == False:
    #             break
    #===========================================================================

    def startPlaying(self, frequency=440.0, amplitude=0.5, framerate=48100, duration=30, bufsize=1024):
        # create stream
        channels = ((wb.sine_wave(frequency, amplitude=amplitude, framerate=framerate),),)
        nframes = framerate * duration
        while self.play:
            try:
                samples = wb.compute_samples(channels, nframes)
                self.audioStream = MyStream(self.audioDev.open(format=self.audioDev.get_format_from_width(2), channels=1, rate=framerate, output=True))
                wb.write_wavefile(self.audioStream, samples, nframes=nframes, sampwidth=2, framerate=framerate, bufsize=bufsize)
            except AttributeError:
                pass
        else:
            self.audioStream.stopIt()
            self.audioDev.terminate()
        return

    def stopPlaying(self):
        self.play = False
        print "Wait for finish current stream"

if __name__ == '__main__':
    from properties.config import ConfigProvider
    config = ConfigProvider().getAudioConfig()
    s = Sound()
    s.startPlaying(float(config['frequency']), float(config['amplitude']), int(config['framerate']), int(config['duration']), int(config['buffersize']))
    s.stopPlaying()

