import pvporcupine
import pyaudio
import struct
import numpy as np
import wave
import math
import pvcobra
import sounddevice as sd
#import wavio as wv
#from scipy.io.wavfile import write

cobra = pvcobra.create(access_key='R/RPKdlOkQv8mSmUef6ccnRV27swlnk/WG0YDg4z56P1ZVToo7HugA==')

porcupine = pvporcupine.create(
  access_key='R/RPKdlOkQv8mSmUef6ccnRV27swlnk/WG0YDg4z56P1ZVToo7HugA==',
  keyword_paths=['./hey-dobby_en_raspberry-pi_v2_1_0.ppn']
)

"""Represents a "frame" of audio data.
Requires the number of bytes, the timestamp of the frame, and the duration on init"""
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
def rms( data ):
    count = len(data)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, data )
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768)
        sum_squares += n*n
    return math.sqrt( sum_squares / count )


def print_sound(indata, outdata, frames, time, status):
    volume_norm = np.linalg.norm(indata)*10
    print ("|" * int(volume_norm))

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

def print_sound(indata, outdata, frames, time, status):
    volume_norm = np.linalg.norm(indata)*10
    #print ("|" * int(volume_norm))
    print(int(volume_norm))

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
    pcm = audio_stream.read(new_frame_number, exception_on_overflow = False)
    pcm = struct.unpack_from("h" * new_frame_number, pcm)
    #print(pcm)
    #print(len(pcm))
    pcm = resample(pcm, 44100)
    #pcm = sd.Stream.read(pcm,44100)


  
    keyword_index = porcupine.process(pcm)
    
    if keyword_index == 0:
        initial_volume=rms(audio_stream.read(44100 , exception_on_overflow = False))
        initial_voice_prob = cobra.process(pcm)
        # detected 'hey dobby'
        print('hey dobby detected!')
        print("initial volume:",initial_volume)
        print("initial voice prob:",initial_voice_prob)
        # the file name output you want to record into
        filename = "recorded.wav"
        # set the chunk size of 1024 samples
        chunk = 44100
        # sample format
        FORMAT = pyaudio.paInt16
        # mono, change to 2 if you want stereo
        channels = 1
        # 44100 samples per second
        sample_rate = 44100

        frames = []
        silence = []

        record_seconds = 50
        auto_stop_condition = 15

        breaker = True
        i = 0
        print("Recording...")
        while breaker and i in range(int(sample_rate / chunk * record_seconds)):
            data = audio_stream.read(chunk , exception_on_overflow = False)
            print(cobra.process(pcm))
            if rms(data)<0.1:
                print(silence)
                #print("volume:",rms(data))
                print("voice prob:",cobra.process(pcm))
                silence.append(1)
            else:
                silence=[]
                print(silence)
            #print(silence)
            if len(silence)==auto_stop_condition:
                breaker = False
            # if you want to hear your voice while recording
            # stream.write(data)
            frames.append(data)
            i+=1
        # frames = pcm
        print("Finished recording.")

        wf = wave.open(filename, "wb")
        # set the channels
        wf.setnchannels(channels)
        # set the sample format
        wf.setsampwidth(pa.get_sample_size(FORMAT))
        # set the sample rate
        wf.setframerate(sample_rate)
        # write the frames as bytes
        wf.writeframes(b"".join(frames))
        # close the file
        wf.close()
    else:
        #print(rms(audio_stream.read(44100 , exception_on_overflow = False)))
        #print(audio_stream.read(44100 , exception_on_overflow = False))
        print('nay')
        #with sd.Stream(callback=print_sound):
        #    sd.sleep(10000)