import pyaudio
import wavebender as wb
from myStream import MyStream
from threading import Thread

class Sound:

    def __init__(self, audioConfig, osConfig):
        self.play = False
        self.audioStream = None
        self.audioConfig = audioConfig
        self.frequency = float(self.audioConfig['frequency'])
        self.amplitude = float(self.audioConfig['amplitude'])
        self.framerate = int(self.audioConfig['framerate'])
        self.duration = int(self.audioConfig['duration'])
        self.bufsize = int(self.audioConfig['buffersize'])
        self.threadNum = 0
        self.osConfig = osConfig

    def startNewThread(self):
        self.t = Thread(name="Soundplayer-" + str(self.threadNum), target=self.startPlaying, args=(self.frequency, self.amplitude, self.framerate, self.duration, self.bufsize))
        self.t.start()
        self.threadNum += 1
        return self.t

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
    def setup(self):
        self.audioDev = pyaudio.PyAudio()
        self.play = True
        if self.osConfig['type'] == 'nt':
            self.isWindows = True
        else:
            self.isWindows = False

    def startPlaying(self, frequency=440.0, amplitude=0.5, framerate=48000, duration=60, bufsize=1024):

        if self.isWindows:
            while True:
                try:
                    import winsound
                    winsound.Beep(int(frequency), duration * 1000)
                except AttributeError:
                    pass
                if self.play == False:
                    break
        else:
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
        print("Wait for finish current stream")

if __name__ == '__main__':
    from properties.config import ConfigProvider
    config = ConfigProvider().getAudioConfig()
    s = Sound()
    s.startPlaying(float(config['frequency']), float(config['amplitude']), int(config['framerate']), int(config['duration']), int(config['buffersize']))
    s.stopPlaying()

