#PPD, fiddle~ notes/drafting

#!apt install libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg
#!pip install pyaudio

import math
import struct
import time
from math import log10
import matplotlib.pyplot as plt

import pyaudio

p=pyaudio.PyAudio()

def decibelScale(value):
    return 20*log10(value)

def levelRMS(data):
    count = len(data)/2
    format = "%dh"%count
    shorts = struct.unpack(format, data)
    sum_squares = 0.0
    for sample in shorts:
        n = sample*(1.0/32678)
        sum_squares += n*n
    return decibelScale(math.sqrt(sum_squares / count))

def callback(in_data, frame_count, time_info, status):
  levels = []
  for _i in range(1024):
    levels.append(struct.unpack('<h', in_data[_i:_i+2])[0])
  avg_chunk = sum(levels)/len(levels)
  print("Level:", avg_chunk, "Time:", time_info['current_time'], "i:", _i, "rms:", levelRMS(in_data))

  #print(levels(stream.read(1024)))

  return (in_data, pyaudio.paContinue)
'''
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                frames_per_buffer=1024,
                input=True,
                output=True,
                stream_callback=callback)

#print(levels(stream.read(1024)))

time.sleep(10)
stream.close()
'''
