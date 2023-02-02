from kasa import SmartBulb
import os
from dotenv import load_dotenv

load_dotenv()
BULB_IP = os.getenv("BULB_IP")

class LightBulb:
    """
    This class is used to control the light bulb.
    """
    async def update(self):
        await self.bulb.update()
    
    def __init__(self):
        self.bulb = SmartBulb(BULB_IP)
        
    async def turn_on(self):
        await self.bulb.turn_on()
        await self.bulb.update()

    async def turn_off(self):
        await self.bulb.turn_off()
        await self.bulb.update()

    async def set_intensity(self, intensity: int):
        await self.bulb.set_brightness(intensity)
        await self.bulb.update()
    
    async def set_hsv(self, hue: int, saturation: int, value: int):
        await self.bulb.set_hsv(hue, saturation, value)
        await self.bulb.update()
