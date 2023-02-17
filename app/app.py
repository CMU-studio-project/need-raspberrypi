from typing import Union, Optional
from pathlib import Path
import time
import json
import asyncio
from bulb_controller import LightBulb
import os

from needpubsub.publish import publish_message
from needpubsub.subscribe import subscribe_message_sync
from audio_controller import AudioController

class NeedApp:
    """
    1. GCP에 오디오 보내서 command 받기
    2. 시간이 지나도 커맨드가 안 오면 로컬 stt+간단한 커맨드 돌리기
    2-1. 놓친 메시지 처리하기 - async로 돌리고, 해당 session 메시지만 ack?
    3. 인터넷 문제로 2도 실패하면 실패 음성 송출
    """
    def __init__(self, project_id: str, device_id: str, topic_id: str):
        self.bulb = LightBulb()
        self.project_id = project_id
        self.device_id = device_id
        self.topic_id = topic_id
        self.subscription_id = f"command-{self.device_id}-sub"
        self.session_id = str(time.time_ns())
        self.audio_controller = AudioController()

    def run(self, debug_audio: Optional[str] = None) -> None:
        while True:
            debug_audio = self.audio_controller.record(True ,"audio/recorded.wav") 
            if debug_audio:
                self.send_audio("./audio/recorded.wav", None)
                self.wait_command()

    def send_audio(self, audio: Union[bytes, Path, str], house: str) -> None:
        if isinstance(audio, (Path, str)):
            with open(audio, "rb") as f:
                audio_bytes = f.read()
        else:
            audio_bytes = audio

        house_kwargs = {"house": house} if house is not None else {}
        publish_message(
            audio_bytes,
            self.project_id,
            self.topic_id,
            device_id=self.device_id,
            session_id=self.session_id,
            audio_ext="wav",
            **house_kwargs,
        )
        
    def wait_command(self) -> None:
        subscribe_message_sync(self.project_id, self.subscription_id, self.sub_callback)

    async def bulb_handler(self, command) -> None:
        if command["power"] != None:
            if command["power"] == "on":
                await self.bulb.turn_on()
            else:
                await self.bulb.turn_off()
        if command["intensity"] != None:
            await self.bulb.set_intensity(int(command["intensity"]))
        elif command["color"] != None:
            await self.bulb.set_hsv(command["color"][0], int(command["color"][1]), int(command["color"][2]))
        if command["power"] != None:
            if command["power"] == "on":
                await self.bulb.turn_on()
            else:
                await self.bulb.turn_off()
    
    def handle_house(self, command) -> None:
        house = command["house"]
        # if house == "gryffindor":
        #     os.system("mpg321 './tts-audio/SortingHat_start.mp3'")
        # else:
        #     os.system("mpg321 './tts-audio/SortingHat_mid.mp3'")
        # os.system("mpg321 './tts-audio/Q_{}.mp3'".format(house))

        # TODO: mic listener로 대체
        mic = AudioController()
        mic.record(False, "audio/recorded.wav")
        self.send_audio("audio/recorded.wav", house=house)
        self.wait_command()

    def sub_callback(self, message: bytes, **kwargs) -> None:
        command = json.loads(message.decode("utf-8"))
        print(command)
        print(kwargs)
        self.session_id = kwargs.get("session_id", str(time.time_ns()))
        print(self.session_id)
        if command["house"] == None:
            asyncio.run(self.bulb_handler(command))
        else:
            asyncio.run(self.handle_house(command))
    