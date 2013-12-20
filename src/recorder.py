import matplotlib
from numpy.lib.utils import deprecate
matplotlib.use('TkAgg')  # <-- THIS MAKES IT FAST!
import numpy as np
import pyaudio
from threading import Timer, Thread
import properties.config as config
import time

class SwhRecorder:
    """Simple, cross-platform class to record from the microphone."""

    def __init__(self, gestureFileIO, frequency=config.frequency):
        """minimal garb is executed when class is loaded."""
        self.frequency = frequency
        self.gestureFileIO = gestureFileIO
        self.FRAMERATE = config.framerate
        self.BUFFERSIZE = config.buffersize
        self.secToRecord = config.secToRecord
        self.timerStop = False
        # frequency range (+ / -)
        frequencyToIndex = self.BUFFERSIZE / (self.FRAMERATE + 0.0)
        self.leftBorder = (frequencyToIndex * frequency) - config.leftBorder
        self.rightBorder = (frequencyToIndex * frequency) + config.rightBorder
        self.transformedData = None
        self.initRecording()

        self.threadNum = 0
        self.setup()

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

        self.xsBuffer = np.arange(self.BUFFERSIZE) * self.secPerPoint
        self.xs = np.arange(self.chunksToRecord * self.BUFFERSIZE) * self.secPerPoint
        self.audio = np.empty((self.chunksToRecord * self.BUFFERSIZE), dtype=np.int16)

    def close(self):
        self.stopRecording()
        """cleanly back out and release sound card."""
        if(not self.waitToFinishCurrentRecord):
            self.audioInStream.stop_stream()
            self.audioInStream.close()
            self.audioDev.terminate()

    ### RECORDING AUDIO ###
    def getAudio(self):
        """get a single buffer size worth of audio."""
        audioString = self.audioInStream.read(self.BUFFERSIZE)
        return np.fromstring(audioString, dtype=np.int16)

    def record(self, intervall=config.recordIntervall):
        """record secToRecord seconds of audio."""
        if self.timerStop:
            return
        self.waitToFinishCurrentRecord = True
        for i in range(self.chunksToRecord):
            self.audio[i * self.BUFFERSIZE:(i + 1) * self.BUFFERSIZE] = self.getAudio()
        self.fft()
        if(self.recordClass is not None):
            self.recordCount -= 1
            self.recordData.append(self.transformedData[1])
            if(self.recordCount == 0):
                self.writeGesture()
                self.initRecording()
        self.waitToFinishCurrentRecord = False
        if(not self.timerStop):
            self.t = Timer(intervall, self.startNewThread).start()
        else:
            self.close()

    def startNewThread(self):
        self.thread = Thread(name="Recorder-" + str(self.threadNum), target=self.record, args=())
        self.thread.start()
        self.threadNum += 1
        return self.thread

    def is_alive(self):
        if self.thread is not None:
            return self.thread.is_alive()
        return False

    def writeGesture(self):
        self.gestureFileIO.writeGesture(self.recordClass, self.recordData)
        self.callback(self.recordClass)

    def initRecording(self):
        self.recordClass = None
        self.recordCount = config.recordingFrames
        self.recordData = []
        self.callback = None

    def stopRecording(self):
        self.timerStop = True

    def setRecordClass(self, recordClass, callback):
        self.recordClass = recordClass
        self.callback = callback

    @deprecate
    def continuousStart(self):
        """CALL THIS to start running forever."""
        self.t = Thread(name="Recorder", target=self.record)
        self.t.start()

    @deprecate
    def continuousEnd(self):
        """shut down continuous recording."""
        self.timerStop = True

    ### MATH ###

    def downsample(self, data, mult):
        """Given 1D data, return the binned average."""
        overhang = len(data) % mult
        if overhang: data = data[:-overhang]
        data = np.reshape(data, (len(data) / mult, mult))
        data = np.average(data, 1)
        return data

    def fft(self, data=None, trimBy=1, logScale=False, divBy=4000):
        # print "fft " + str(time.time())
        data = self.audio.flatten()
        left, right = np.split(np.abs(np.fft.fft(data)), 2)
        ys = np.add(left, right[::-1])
        ys = ys[self.leftBorder:self.rightBorder]
        if logScale:
            ys = np.multiply(20, np.log10(ys))
        xs = np.arange(self.BUFFERSIZE / 2, dtype=float)
        xs = xs[self.leftBorder:self.rightBorder]
        if trimBy:
            i = int((self.BUFFERSIZE / 2) / trimBy)
            ys = ys[:i]
            xs = xs[:i] * self.FRAMERATE / self.BUFFERSIZE
        if divBy:
            ys = ys / float(divBy)
        """ frequency to index-> frequency * BUFFERSIZE / FRAMERATE """
        self.transformedData = xs, ys

    def getTransformedData(self):
        # print "get " + str(time.time())
        return self.transformedData

