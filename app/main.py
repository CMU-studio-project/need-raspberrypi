from audio_controller import AudioController
from bulb_controller import LightBulb
from dotenv import load_dotenv
from app import NeedApp
import os
import asyncio
import pyaudio
import struct
import numpy as np
import wave
import sounddevice as sd

# Internet, GCP, bulb connection status check
os.system("python error_cases.py")

load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")
TOPIC_ID = os.getenv("TOPIC_ID")
DEVICE_ID = os.getenv("DEVICE_ID")
GOOGLE_APPLICATION_CREDENTIAL = os.getenv("GOOGLE_APPLICATION_CREDENTIAL")

def record(hotword : bool = True, filename: str = "./audio/recorded.wav"):
    audio_set = AudioController()
    pa = pyaudio.PyAudio()
    new_frame_number = int(audio_set.porcupine.frame_length * 441 / 160)

    volume_queue=[]
    voice_prob_queue=[]
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

    while True:
        if os.path.exists("./audio/ravenclaw.txt"):
            hotword = False
            house = "ravenclaw"
            filename = "./audio/ravenclaw.wav"
        elif os.path.exists("./audio/hufflepuff.txt"):
            hotword = False
            house = "hufflepuff"
            filename = "./audio/hufflepuff.wav"
        elif os.path.exists("./audio/slytherin.txt"):
            hotword = False
            house = "slytherin"
            filename = "./audio/slytherin.wav"
        elif os.path.exists("./audio/gryffindor.txt"):
            hotword = False
            house = "gryffindor"
            filename = "./audio/gryffindor.wav"
        else:
            hotword = True
            house = None
            filename = "./audio/recorded.wav"

        pcm = audio_stream.read(new_frame_number, exception_on_overflow = False)
        numpydata = np.frombuffer(pcm, dtype=np.int16)
        pcm = struct.unpack_from("h" * new_frame_number, pcm)
        pcm = audio_set.resample(pcm, 44100)

        keyword_index = audio_set.porcupine.process(pcm)
        
        if keyword_index == 0 or not hotword:
            if hotword:
                os.system("mpg321 './tts-audio/dobby_is_here.mp3'")

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

                if audio_set.rms(data)<0.1:
                    print("voice prob:",audio_set.cobra.process(pcm))
                    silence.append(1)
                else:
                    silence=[]
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
            
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIAL
            app = NeedApp(PROJECT_ID, DEVICE_ID, TOPIC_ID)
            if hotword == False:
                app.run(filename, house)
            else:
                app.run(filename, None)
        else:
            pass

if __name__ == "__main__":  
    record()
       