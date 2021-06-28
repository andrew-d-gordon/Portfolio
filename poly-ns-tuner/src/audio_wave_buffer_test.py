# IMPORTS
import pyaudio
import wave
import struct
from main import poly_note_tuner
import sys
from poly_note_detection import fft_plot, compute_ft
import numpy as np

# CONSTANTS
CHUNK = 4096
wf = wave.open('samples/piano_chords_melody_Cm_vanilla_16.wav', 'rb')
wf_sr = wf.getframerate()
q = 5  # window to analyze in seconds
c = 12  # number of time windows to process
sf = 1.5  # signal scale factor

# Instantiate PyAudio
p = pyaudio.PyAudio()

# Open Stream
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                frames_per_buffer=CHUNK,
                rate=wf_sr,
                output=True,
                input=False)

# read data
data = wf.readframes(CHUNK)

sizes = {1: 'B', 2: 'h', 4: 'i'}
channels = wf.getnchannels()
fmt_size = sizes[wf.getsampwidth()]
# fmt = "<" + fmt_size*channels

# play stream (3)
while len(data) > 0:
    stream.write(data)
    data = wf.readframes(CHUNK)
    print(len(data))

    fmt = "<{0}h".format(2*CHUNK)
    data_int = struct.unpack(fmt, data)
    poly_note_tuner(data_int, wf_sr)
    # print(data_int)


# stop stream (4)
stream.stop_stream()
stream.close()

# close PyAudio (5)
p.terminate()