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
import time


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

if __name__ == '__main__':

    audio_controller = AudioController()

    new_frame_number = int(audio_controller.porcupine.frame_length * 441 / 160)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = audio_controller.GOOGLE_APPLICATION_CREDENTIAL
    app = NeedApp(audio_controller.PROJECT_ID, audio_controller.DEVICE_ID, audio_controller.TOPIC_ID)
    start_time = time.time()
    app.run('audio/turn_off_file.wav')
    end_time = time.time()
    print(end_time - start_time)
