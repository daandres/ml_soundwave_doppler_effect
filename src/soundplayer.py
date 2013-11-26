import pyaudio
# # To use wavebender checkout this repo: https://github.com/zacharydenton/wavebender.git and install it with python setup.py
from wavebender import *

p = pyaudio.PyAudio()
stream = None

def playsound(frequency=440.0, amplitude=0.5, framerate=44100, duration=30):
    stream = p.open(format=p.get_format_from_width(2), channels=1, rate=framerate, output=True)
    channels = ((sine_wave(frequency, amplitude=amplitude, framerate=framerate),),)
    samples = compute_samples(channels, framerate * duration * 1)
    write_wavefile(stream, samples)


def stop():
    stream.stop_stream()
    stream.close()
    p.terminate()
    
if __name__ == '__main__':
    playsound(21000.0, framerate=48100, duration=30)

