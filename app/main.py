import os
import pvporcupine
import pyaudio
import struct
import numpy as np
import wave
import math
import pvcobra
from dotenv import load_dotenv
from app import NeedApp
import sounddevice as sd


class AudioController:
    def __init__(self):
        load_dotenv()
        self.PROJECT_ID = os.getenv("PROJECT_ID")
        self.DEVICE_ID = os.getenv("DEVICE_ID")
        self.TOPIC_ID = os.getenv("TOPIC_ID")
        self.GOOGLE_APPLICATION_CREDENTIAL = os.getenv("GOOGLE_APPLICATION_CREDENTIAL")
        self.cobra = pvcobra.create(access_key='R/RPKdlOkQv8mSmUef6ccnRV27swlnk/WG0YDg4z56P1ZVToo7HugA==')

        self.porcupine = pvporcupine.create(
        access_key='R/RPKdlOkQv8mSmUef6ccnRV27swlnk/WG0YDg4z56P1ZVToo7HugA==',
        keyword_paths=['./audio/hey-dobby_en_raspberry-pi_v2_1_0.ppn'])

        self.porcupine2 = pvporcupine.create(
        access_key='xMMjYslGKCWniL+vZz61i/XTVGTB5vrrsxi11C7q7g/dhBTJxkd84g==',
        keyword_paths=['./ko_raspberry-pi_v2_1_1.ppn'],
        model_path="./audio/porcupine_params_ko.pv")
        

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

if __name__ == '__main__':

    audio_controller = AudioController()

    pa = pyaudio.PyAudio()

    new_frame_number = int(audio_controller.porcupine.frame_length * 441 / 160)

    audio_stream=pa.open(
        # rate=porcupine.sample_rate,
        rate = 44100,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer= new_frame_number)

    while True:
        pcm = audio_stream.read(new_frame_number, exception_on_overflow = False)
        numpydata = np.frombuffer(pcm, dtype=np.int16)
        pcm = struct.unpack_from("h" * new_frame_number, pcm)
        pcm = audio_controller.resample(pcm, 44100)

        volume_queue.insert(0, np.linalg.norm(numpydata))
        voice_prob_queue.insert(0, cobra.process(pcm))
        if len(volume_queue) > 20:
            volume_queue.pop()
            voice_prob_queue.pop()
        
        #print(int(np.linalg.norm(numpydata)/10000)*"|")

        keyword_index = audio_controller.porcupine.process(pcm)
        keyword_index2 = porcupine2.process(pcm)
        
        if keyword_index == 0:

            #핫워드가 포착되는 순간은 오히려 "hey dobby"가 끝나는 시점이기 때문에 발음을 시작하던 순간을 기준으로 잡음
            initial_voice_prob  = sorted(voice_prob_queue)[-5]
            #initial_volume      = sorted(volume_queue)[-10]
            initial_volume      = volume_queue[voice_prob_queue.index(sorted(voice_prob_queue)[-5]) + 1]
            # detected 'hey dobby'
            print('hey dobby detected!')
            print("initial volume:",initial_volume)
            print("initial voice prob:",initial_voice_prob)

            # the file name output you want to record into
            filename = "audio/recorded.wav"
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
            auto_stop_condition = 4

            breaker = True
            i = 0
            print("Recording...")
            while breaker and i in range(int(sample_rate / chunk * record_seconds)):
                data = audio_stream.read(chunk , exception_on_overflow = False)

                print(audio_controller.cobra.process(pcm))
                if np.linalg.norm(np.frombuffer(audio_stream.read(new_frame_number, exception_on_overflow = False), dtype=np.int16)) < initial_volume and cobra.process(pcm) < initial_voice_prob:
                    print("||||" * (len(silence) + 1))
                    print("voice prob:",cobra.process(pcm))
                    print("volume:",np.linalg.norm(np.frombuffer(audio_stream.read(new_frame_number, exception_on_overflow = False), dtype=np.int16)))
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

            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = audio_controller.GOOGLE_APPLICATION_CREDENTIAL
            app = NeedApp(audio_controller.PROJECT_ID, audio_controller.DEVICE_ID, audio_controller.TOPIC_ID)
            app.run(filename)
        elif keyword_index2 == 0:
        
            # detected 'hey dobby'
            print('도비야 detected!')

            print(volume_queue)
            print(voice_prob_queue)

            #핫워드가 포착되는 순간은 오히려 "hey dobby"가 끝나는 시점이기 때문에 발음을 시작하던 순간을 기준으로 잡음
            initial_voice_prob  = sorted(voice_prob_queue)[-5]
            #initial_volume      = sorted(volume_queue)[-10]
            initial_volume      = volume_queue[voice_prob_queue.index(sorted(voice_prob_queue)[-5]) + 1]

            print("initial voice prob:", initial_voice_prob)
            print("initial volume:", initial_volume)

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

            record_seconds = 10000

            auto_stop_condition = 30

            breaker = True
            i = 0
            print("Recording...")
            while breaker and i in range(int(sample_rate / chunk * record_seconds)):
            
                data = audio_stream.read(44100, exception_on_overflow = False)

                if np.linalg.norm(np.frombuffer(audio_stream.read(new_frame_number, exception_on_overflow = False), dtype=np.int16)) < initial_volume and cobra.process(pcm) < initial_voice_prob:
                    print("||||" * (len(silence) + 1))
                    print("voice prob:",cobra.process(pcm))
                    print("volume:",np.linalg.norm(np.frombuffer(audio_stream.read(new_frame_number, exception_on_overflow = False), dtype=np.int16)))
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
                i += 1
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
            pass
    