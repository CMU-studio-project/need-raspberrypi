import asyncio
from kasa import SmartBulb
import os
from dotenv import load_dotenv

load_dotenv()
BULB_IP = os.getenv("BULB_IP")

async def main():
    
    bulb = SmartBulb(BULB_IP)  # Create an instance of the bulb
    await bulb.update()  # Request the update
    print(bulb.alias)  # Print out the alias
    print(bulb.emeter_realtime)  # Print out current emeter status
    
    await bulb.turn_off()
    await bulb.turn_on()
    await bulb.update()
    print(bulb.is_on)

    await bulb.set_brightness(20)
    await bulb.update()
    await bulb.set_brightness(50)
    await bulb.update()
    await bulb.set_brightness(100)
    await bulb.update()

    await bulb.set_hsv(180, 100, 80)
    await bulb.update()
    print(bulb.hsv)

    await bulb.turn_off()  # Turn the device off

if __name__ == "__main__":
    asyncio.run(main())
