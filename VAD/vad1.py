import pvporcupine
import pyaudio
import struct
import numpy as np

porcupine = pvporcupine.create(
  access_key='R/RPKdlOkQv8mSmUef6ccnRV27swlnk/WG0YDg4z56P1ZVToo7HugA==',
  keyword_paths=['./hey-dobby_en_raspberry-pi_v2_1_0.ppn']
)

"""Represents a "frame" of audio data.
Requires the number of byes, the timestamp of the frame, and the duration on init"""
class Frame(object):
   def __init__(self, bytes, timestamp, duration):
       self.bytes = bytes
       self.timestamp = timestamp
       self.duration = duration

"""Generates audio frames from PCM audio data.
Input: the desired frame duration in milliseconds, the PCM data, and
the sample rate.
Yields/Generates: Frames of the requested duration.
"""
def resample(data, input_rate=44100):
    """
    Microphone may not support our native processing sampling rate, so
    resample from input_rate to RATE_PROCESS here for webrtcvad and
    deepspeech

    Args:
        data (binary): Input audio stream
        input_rate (int): Input audio rate to resample from
    """
    desired_rate = 16000

    resampled_len = int(len(data) * desired_rate / input_rate)
    res = [data[int(i * input_rate / desired_rate)] for i in range(resampled_len)]
    return  res + [res[-1]]


pa = pyaudio.PyAudio()

new_frame_number = int(porcupine.frame_length * 441 / 160)

audio_stream=pa.open(
    # rate=porcupine.sample_rate,
    rate = 44100,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer= new_frame_number)

while True:
    pcm = audio_stream.read(new_frame_number)
    pcm = struct.unpack_from("h" * new_frame_number, pcm)
    #print(pcm)
    #print(len(pcm))
    pcm = resample(pcm, 44100)
  
    keyword_index = porcupine.process(pcm)
    if keyword_index == 0:
        # detected 'hey dobby'
        print('hey dobby detected!')
    else:
        print('nay')