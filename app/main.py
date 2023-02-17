from audio_controller import AudioController
from dotenv import load_dotenv
import os
from app import NeedApp

# # Internet, GCP, bulb connection status check
# os.system("python error_cases.py")

load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")
TOPIC_ID = os.getenv("TOPIC_ID")
DEVICE_ID = os.getenv("DEVICE_ID")
GOOGLE_APPLICATION_CREDENTIAL = os.getenv("GOOGLE_APPLICATION_CREDENTIAL")

if __name__ == "__main__":  
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIAL
    app = NeedApp(PROJECT_ID, DEVICE_ID, TOPIC_ID)
    app.run()
       