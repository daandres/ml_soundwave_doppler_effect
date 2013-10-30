def playsound(frequency, duration):
    import math
    import pyaudio
    
    PyAudio = pyaudio.PyAudio
    RATE = 16000
    WAVE = frequency
    data = ''.join([chr(int(math.sin(x / ((RATE / WAVE) / math.pi)) * 127 + 128)) for x in xrange(RATE)])
    p = PyAudio()
    
    stream = p.open(format=
                    p.get_format_from_width(1),
                    channels=1,
                    rate=RATE,
                    output=True)
    for DISCARD in xrange(duration):
        stream.write(data)
    stream.stop_stream()
    stream.close()
    p.terminate()


def main():
    playsound(300, 30)
    pass

if __name__ == '__main__':
    main()
