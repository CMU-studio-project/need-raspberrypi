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

    def record(self, hotword : bool = True, filename: str = "audio/recorded.wav"):
        
        pa = pyaudio.PyAudio()
        recorded = False
        new_frame_number = int(self.porcupine.frame_length * 441 / 160)

        audio_stream=pa.open(
            # rate=porcupine.sample_rate,
            rate = 44100,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer= new_frame_number)

        volume_queue=[]
        voice_prob_queue=[]
        # # 마이크를 작동시키는 부분인데, 마이크 연결을 try 로 진행하고, 마이크 연결이 안되어있을 때는 except 구문에서 (마이크 연결이 안되어있다는) 에러 음성을 송출.
        # try:
        #     audio_stream=pa.open(
        #         # rate=porcupine.sample_rate,
        #         rate = 44100,
        #         channels=1,
        #         format=pyaudio.paInt16,
        #         input=True,
        #         frames_per_buffer= new_frame_number)
        # except:
        #     bulb = LightBulb()
        #     asyncio.run(bulb.blink_when_error())
        #     os.system("mpg321 './tts-audio/error7_mic.mp3'")

        pcm = audio_stream.read(new_frame_number, exception_on_overflow = False)
        numpydata = np.frombuffer(pcm, dtype=np.int16)
        pcm = struct.unpack_from("h" * new_frame_number, pcm)
        pcm = self.resample(pcm, 44100)

        a = self.cobra.process(pcm)
        b = np.linalg.norm(numpydata)

        print("voice prob:",a)
        print("volume:",b)
        volume_queue.insert(0, b)
        voice_prob_queue.insert(0, a)
        if len(volume_queue) > 20:
            volume_queue.pop()
            voice_prob_queue.pop()

        keyword_index = self.porcupine.process(pcm)
        
        if keyword_index == 0 or not hotword:
            print("volume_queue:",volume_queue)
            print("voice_prob_queue:",voice_prob_queue)
            initial_voice_prob  = sorted(voice_prob_queue)[-5]
            initial_volume      = volume_queue[voice_prob_queue.index(sorted(voice_prob_queue)[-5]) + 1]
            # detected 'hey dobby'
            if hotword:
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
            record_speed = 10

            record_seconds *= record_speed 
            auto_stop_condition *= record_speed 

            breaker = True
            i = 0
            print("Recording...")
            while breaker and i in range(int(sample_rate / chunk * record_seconds)):
                data = audio_stream.read(int(10000 / record_speed) , exception_on_overflow = False)

                current_voice_prob = self.cobra.process(pcm)
                current_volume = np.linalg.norm(np.frombuffer(audio_stream.read(new_frame_number, exception_on_overflow = False), dtype=np.int16))
                
                if current_voice_prob < initial_voice_prob and current_volume < initial_volume:
                    print("||||" * (len(silence) + 1))
                    print("voice prob:",current_voice_prob)
                    print("volume:",current_volume)
                    silence.append(1)
                else:
                    silence=[]
                    print("")
                    print("voice prob:",current_voice_prob)
                    print("volume:",current_volume)
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
            wf.setnchannels(channels)
            wf.setsampwidth(pa.get_sample_size(FORMAT))
            wf.setframerate(sample_rate)
            wf.writeframes(b"".join(frames))
            wf.close()
            recorded = True
            return recorded
        else:
            pass

