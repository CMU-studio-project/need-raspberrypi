import os
import pvporcupine
import pyaudio
import struct
import numpy as np
import wave
import math
import pvcobra
import sounddevice as sd
from bulb_controller import LightBulb
import asyncio

class AudioController:
    def __init__(self):
        self.cobra = pvcobra.create(access_key='R/RPKdlOkQv8mSmUef6ccnRV27swlnk/WG0YDg4z56P1ZVToo7HugA==')

        self.porcupine = pvporcupine.create(
        access_key='R/RPKdlOkQv8mSmUef6ccnRV27swlnk/WG0YDg4z56P1ZVToo7HugA==',
        keyword_paths=['./audio/hey-dobby_en_raspberry-pi_v2_1_0.ppn']
        )

    """Generates audio frames from PCM audio data.
    Input: the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields/Generates: Frames of the requested duration.
    """
    def rms( self, data ):
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

    def resample(self, data, input_rate=44100):
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

    def hotword_record(self, filename: str = "audio/recorded.wav"):
        pa = pyaudio.PyAudio()

        new_frame_number = int(self.porcupine.frame_length * 441 / 160)

        # audio_stream=pa.open(
        #     # rate=porcupine.sample_rate,
        #     rate = 44100,
        #     channels=1,
        #     format=pyaudio.paInt16,
        #     input=True,
        #     frames_per_buffer= new_frame_number)

        # 마이크를 작동시키는 부분인데, 마이크 연결을 try 로 진행하고, 마이크 연결이 안되어있을 때는 except 구문에서 (마이크 연결이 안되어있다는) 에러 음성을 송출.
        try:
            audio_stream=pa.open(
                # rate=porcupine.sample_rate,
                rate = 44100,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer= new_frame_number)
        except:
            bulb = LightBulb()
            asyncio.run(bulb.blink_when_error())
            os.system("mpg321 './tts-audio/error7_mic.mp3'")

        pcm = audio_stream.read(new_frame_number, exception_on_overflow = False)
        pcm = struct.unpack_from("h" * new_frame_number, pcm)
        pcm = self.resample(pcm, 44100)

        keyword_index = self.porcupine.process(pcm)
        
        if keyword_index == 0:
            initial_volume=self.rms(audio_stream.read(44100 , exception_on_overflow = False))
            initial_voice_prob = self.cobra.process(pcm)
            # detected 'hey dobby'
            os.system("mpg321 './tts-audio/dobby_is_here.mp3'")
            print("initial volume:",initial_volume)
            print("initial voice prob:",initial_voice_prob)

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

            record_seconds = 15
            auto_stop_condition = 3

            breaker = True
            i = 0
            print("Recording...")
            while breaker and i in range(int(sample_rate / chunk * record_seconds)):
                data = audio_stream.read(chunk , exception_on_overflow = False)

                print(self.cobra.process(pcm))
                if self.rms(data)<0.1:
                    print(silence)
                    #print("volume:",rms(data))
                    print("voice prob:",self.cobra.process(pcm))
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
            return True
        else:
            pass

    def record_and_save(self, filename: str = "audio/result.wav"):
        pa = pyaudio.PyAudio()

        new_frame_number = int(self.porcupine.frame_length * 441 / 160)

        # 마이크를 작동시키는 부분인데, 마이크 연결을 try 로 진행하고, 마이크 연결이 안되어있을 때는 except 구문에서 (마이크 연결이 안되어있다는) 에러 음성을 송출.
        try:
            audio_stream=pa.open(
                # rate=porcupine.sample_rate,
                rate = 44100,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer= new_frame_number)
        except:
            bulb = LightBulb()
            asyncio.run(bulb.blink_when_error())
            os.system("mpg321 './tts-audio/error7_mic.mp3'")

        pcm = audio_stream.read(new_frame_number, exception_on_overflow = False)
        pcm = struct.unpack_from("h" * new_frame_number, pcm)
        pcm = self.resample(pcm, 44100)

        initial_volume=self.rms(audio_stream.read(44100 , exception_on_overflow = False))
        initial_voice_prob = self.cobra.process(pcm)

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

        record_seconds = 15
        auto_stop_condition = 3

        breaker = True
        i = 0
        print("Recording...")
        while breaker and i in range(int(sample_rate / chunk * record_seconds)):
            data = audio_stream.read(chunk , exception_on_overflow = False)

            print(self.cobra.process(pcm))
            if self.rms(data)<0.1:
                print(silence)
                #print("volume:",rms(data))
                print("voice prob:",self.cobra.process(pcm))
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
