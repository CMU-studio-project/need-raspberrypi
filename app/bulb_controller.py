from kasa import SmartBulb
import os
from dotenv import load_dotenv
import asyncio

class LightBulb:
    """
    This class is used to control the light bulb.
    """
    def __init__(self):
        load_dotenv()
        self.BULB_IP = os.getenv("BULB_IP")
        self.bulb = SmartBulb(self.BULB_IP)
        
    async def turn_on(self):
        await self.bulb.turn_on()
        await self.bulb.update()

    async def turn_off(self):
        await self.bulb.turn_off()
        await self.bulb.update()

    async def set_intensity(self, intensity: int):
        await self.bulb.turn_on()
        await self.bulb.update()
        bright = self.bulb.brightness
        if int(bright) == 100 and intensity>0:
            os.system("mpg321 './tts-audio/error5_bulb_max.mp3'")
        elif int(bright) == 0 and intensity<0:
            os.system("mpg321 './tts-audio/error6_bulb_min.mp3'")
        else: 
            new_bright = intensity + int(bright)
            if new_bright > 100:
                new_bright = 100
            elif new_bright < 0:
                new_bright = 0
            await self.bulb.set_brightness(new_bright)
            await self.bulb.update()
    
    async def set_hsv(self, hue: int, saturation: int, value: int):
        await self.bulb.turn_on()
        await self.bulb.update()
        await self.bulb.set_hsv(hue, saturation, value)
        await self.bulb.update()

    async def get_light_state(self) -> int:
        return self.bulb.brightness
    
    async def blink_when_error(self):
            await self.bulb.update()
            await self.bulb.set_hsv(350, 94, 99) # changing color to scarlet
            await self.bulb.update()
            await self.bulb.turn_on()
            await asyncio.sleep(0.3)
            await self.bulb.turn_off()
            await asyncio.sleep(0.3)
            await self.bulb.turn_on()
            await asyncio.sleep(0.3)
            await self.bulb.turn_off()
            await asyncio.sleep(0.3)
            await self.bulb.turn_on()
            await asyncio.sleep(0.3)
            await self.bulb.turn_off()
            await asyncio.sleep(0.3)