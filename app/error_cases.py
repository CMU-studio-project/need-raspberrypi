import os
# #%%
# Error1. Internet is disconnected
import urllib.request
def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

if not connect():
    os.system("mpg321 './tts-audio/error1_internet.mp3'")


#%%
# Error2. GCP is not working
message = os.system("curl metadata.google.internal -i")
# print(message)
# print(type(message))
if not message[2][-6:] == 'Google':
    os.system("mpg321 './tts-audio/error2_GCP.mp3''")

#%%
# Error3. Command is not understood # sentiment 분석을 대신 하기 때문에 사실 에러 케이스에 해당하지 않음.

# os.system("mpg321 '/home/pi7/Error_message/error3_command.wav'")


#%% Error4. Bulb is not connected
from bulb_controller import LightBulb
bulb = LightBulb()
if bulb.BULB_IP is None:
    os.system("mpg321 '/home/pi7/Error_message/error4_bulb.wav'")


#%%
# Error 5-1. Bulb is already fully bright # app.py 에서 직접 구현함.
# os.system("mpg321 '/home/pi7/Error_message/error5_bulb_max.wav'")

#%%
# Error 5-2. Bulb is already fully dark
# os.system("mpg321 '/home/pi7/Error_message/error5_bulb_min.wav'")


#%%
# # Error 6. Mike is not connected  # audio_controller.py 에서 구현함.

# try:
#     os.system("rm out1.log")    
# except:
#     pass


# os.system("lsusb | tee -a out1.log")
# testFile = open('out1.log','rt')

# fileLines = testFile.readlines()

# testFile.close()

# if len(fileLines) == 4:
#     os.system("mpg321 '/home/pi7/Error_message/error7_mike.wav'") # 오디오 재생 대신에 전구 깜빡이는 것으로 바꾸면 됨.

