import matplotlib
matplotlib.use('TkAgg')  # <-- THIS MAKES IT FAST!
import numpy
import pyaudio
import threading

class SwhRecorder:
    """Simple, cross-platform class to record from the microphone."""

    def __init__(self, frequency=21000, fRange=500):
        """minimal garb is executed when class is loaded."""
        self.frequency = frequency
        self.FRAMERATE = 48100
        self.BUFFERSIZE = 2 ** 12  # 1024 is a good buffer size
        self.secToRecord = .01
        self.threadsDieNow = False
        self.newAudio = False
        # frequency range (+ / -)
        frequenyToIndex = self.BUFFERSIZE / (self.FRAMERATE + 0.0)
        self.leftBorder = frequenyToIndex * (frequency - fRange)
        self.rightBorder = frequenyToIndex * (frequency + fRange)


    def setup(self):
        """initialize sound card."""
        # TODO - windows detection vs. alsa or something for linux
        # TODO - try/except for sound card selection/initiation

        self.buffersToRecord = int(self.FRAMERATE * self.secToRecord / self.BUFFERSIZE)
        if self.buffersToRecord == 0: self.buffersToRecord = 1
        self.samplesToRecord = int(self.BUFFERSIZE * self.buffersToRecord)
        self.chunksToRecord = int(self.samplesToRecord / self.BUFFERSIZE)
        self.secPerPoint = 1.0 / self.FRAMERATE

        self.audioDev = pyaudio.PyAudio()
        self.audioInStream = self.audioDev.open(format=pyaudio.paInt16, channels=1, rate=self.FRAMERATE, input=True, frames_per_buffer=self.BUFFERSIZE)

        self.xsBuffer = numpy.arange(self.BUFFERSIZE) * self.secPerPoint
        self.xs = numpy.arange(self.chunksToRecord * self.BUFFERSIZE) * self.secPerPoint
        self.audio = numpy.empty((self.chunksToRecord * self.BUFFERSIZE), dtype=numpy.int16)

    def close(self):
        """cleanly back out and release sound card."""
        self.continuousEnd()
        self.audioInStream.stop_stream()
        self.audioInStream.close()
        self.audioDev.terminate()

    ### RECORDING AUDIO ###

    def getAudio(self):
        """get a single buffer size worth of audio."""
        audioString = self.audioInStream.read(self.BUFFERSIZE)
        return numpy.fromstring(audioString, dtype=numpy.int16)

    def record(self, forever=True):
        """record secToRecord seconds of audio."""
        while True:
            if self.threadsDieNow: break
            for i in range(self.chunksToRecord):
                self.audio[i * self.BUFFERSIZE:(i + 1) * self.BUFFERSIZE] = self.getAudio()
            self.newAudio = True
            if forever == False: break

    def continuousStart(self):
        """CALL THIS to start running forever."""
        self.t = threading.Thread(target=self.record)
        self.t.start()

    def continuousEnd(self):
        """shut down continuous recording."""
        self.threadsDieNow = True

    ### MATH ###

    def downsample(self, data, mult):
        """Given 1D data, return the binned average."""
        overhang = len(data) % mult
        if overhang: data = data[:-overhang]
        data = numpy.reshape(data, (len(data) / mult, mult))
        data = numpy.average(data, 1)
        return data

    def fft(self, data=None, trimBy=1, logScale=False, divBy=4000):
        if data == None:
            data = self.audio.flatten()
        left, right = numpy.split(numpy.abs(numpy.fft.fft(data)), 2)
        ys = numpy.add(left, right[::-1])
        ys = ys[self.leftBorder:self.rightBorder]
        if logScale:
            ys = numpy.multiply(20, numpy.log10(ys))
        xs = numpy.arange(self.BUFFERSIZE / 2, dtype=float)
        xs = xs[self.leftBorder:self.rightBorder]
        if trimBy:
            i = int((self.BUFFERSIZE / 2) / trimBy)
            ys = ys[:i]
            xs = xs[:i] * self.FRAMERATE / self.BUFFERSIZE
        if divBy:
            ys = ys / float(divBy)
        """ frequency to index-> frequency * BUFFERSIZE / FRAMERATE """
        return xs, ys

    def getNewAudio(self):
        return self.newAudio    

    def setNewAudio(self, newAudio):
        self.newAudio = newAudio 
