from typing import Union, Optional
from pathlib import Path
import time
import json
import asyncio
from bulb_controller import LightBulb
# from flask import Flask

from needpubsub.publish import publish_message
from needpubsub.subscribe import subscribe_message_sync

# app = Flask(__name__)

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

    def run(self, debug_audio: Optional[str] = None) -> None:
        if debug_audio is not None:
            self.send_audio(debug_audio)
            self.wait_command()

    def send_audio(self, audio: Union[bytes, Path, str]):
        if isinstance(audio, (Path, str)):
            with open(audio, "rb") as f:
                audio_bytes = f.read()
        else:
            audio_bytes = audio
        
        session_id = str(time.time_ns())
        publish_message(
            audio_bytes,
            self.project_id,
            self.topic_id,
            device_id=self.device_id,
            session_id=session_id,
        )
        
    def wait_command(self) -> None:
        subscribe_message_sync(self.project_id, self.subscription_id, self.sub_callback)

    async def bulb_handler(self, command) -> None:
        if command["intensity"] != "None":
            await self.bulb.turn_on()
            await self.bulb.set_intensity(command["intensity"])
        elif command["color"] != "None":
            await self.bulb.turn_on()
            await self.bulb.set_hsv(command["color"][0], int(command["color"][1]), int(command["color"][2]))
        if command["power"] != "None":
            if command["power"] == "on":
                await self.bulb.turn_on()
            else:
                await self.bulb.turn_off()   
            
    def sub_callback(self, message: bytes, **kwargs) -> None:
        command = json.loads(message.decode("utf-8"))
        print(command)
        print(kwargs)
        asyncio.run(self.bulb_handler(command))
       
    
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--device_id", type=str, help="Device ID")
    parser.add_argument("--project_id", type=str, help="project ID")
    parser.add_argument("--topic_id", type=str, help="topic ID")
    parser.add_argument("--debug_audio", type=str, help="Audio file for debugging")
    args = parser.parse_args()
    
    app = NeedApp(args.project_id, args.device_id, args.topic_id)
    app.run(args.debug_audio)
   