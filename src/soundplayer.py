import pyaudio
## To use wavebender checkout this repo: https://github.com/zacharydenton/wavebender.git and install it with python setup.py
from wavebender import *

def playsound(frequency, duration):
    PyAudio = pyaudio.PyAudio

    RATE = 44100
    p = PyAudio()
      
    stream = p.open(format=
                    p.get_format_from_width(2),
                    channels=1,
                    rate=RATE,
                    output=True)
    channels = ((sine_wave(frequency),),)
    samples = compute_samples(channels, RATE * duration * 1)
    write_wavefile(stream, samples)
    stream.stop_stream()
    stream.close()
    p.terminate()



def main():
    playsound(19000.0, 30)
    pass

if __name__ == '__main__':
    main()
