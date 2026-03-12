
import os
import re
import time
import logging
import requests
import speech_recognition as sr
from datetime import datetime
from typing import Dict, Optional, Any
import sys
import io

# Force UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# 1. CONFIGURATION
# ==========================================
class Config:
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', 'YOUR_WEATHER_API_KEY')
    EMAIL_API_KEY = os.getenv('EMAIL_API_KEY', 'YOUR_EMAIL_API_KEY')
    SMART_HOME_API_KEY = os.getenv('SMART_HOME_API_KEY', 'YOUR_SMART_HOME_API_KEY')
    LANGUAGE = 'en-US'
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'default_secret_key')

# ==========================================
# 2. SECURITY MODULE
# ==========================================
class SecurityManager:
    def __init__(self, key: str):
        self.key = key.encode()
    
    def encrypt(self, data: str) -> str:
        return ''.join(chr(ord(c) ^ ord(self.key[i % len(self.key)])) for i, c in enumerate(data))
    
    def decrypt(self, data: str) -> str:
        return ''.join(chr(ord(c) ^ ord(self.key[i % len(self.key)])) for i, c in enumerate(data))

# ==========================================
# 3. API INTEGRATIONS
# ==========================================
class WeatherAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, location: str) -> str:
        try:
            params = {'q': location, 'appid': self.api_key, 'units': 'metric'}
            response = requests.get(self.base_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                return f"Weather in {data['name']}: {temp}°C, {desc}"
            return "Unable to fetch weather data."
        except Exception as e:
            logger.error(f"Weather API Error: {e}")
            return "Weather service unavailable."

class EmailAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def send(self, recipient: str, subject: str, body: str) -> str:
        logger.info(f"Sending email to {recipient}: {subject}")
        return f"Email sent to {recipient}."

class SmartHomeAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.devices = {"living_room_light": "off", "thermostat": "22"}

    def control(self, device: str, action: str) -> str:
        if device in self.devices:
            self.devices[device] = action
            return f"Set {device} to {action}."
        return f"Device {device} not found."

# ==========================================
# 4. NLP ENGINE (Keyword-Based)
# ==========================================
class NLPEngine:
    def __init__(self):
        self.custom_commands = {
            "hello": "Hello! How can I help you?",
            "time": f"The current time is {datetime.now().strftime('%H:%M')}",
            "date": f"Today is {datetime.now().strftime('%A, %B %d')}",
            "help": "Commands: weather, email, reminder, light, time, date, help"
        }

    def classify(self, text: str) -> tuple:
        text_lower = text.lower()
        
        # Check Custom Commands
        for trigger, response in self.custom_commands.items():
            if trigger in text_lower:
                return 'custom', response, {}

        # Keyword Matching
        if 'email' in text_lower and ('send' in text_lower or 'write' in text_lower):
            return 'send_email', None, {}
        elif 'weather' in text_lower:
            return 'weather', None, {}
        elif 'reminder' in text_lower or 'remind' in text_lower:
            return 'set_reminder', None, {}
        elif 'light' in text_lower or 'smart' in text_lower or 'home' in text_lower:
            return 'smart_home', None, {}
        
        return 'general', None, {}

    def extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        entities = {}
        text_lower = text.lower()
        
        if intent == 'send_email':
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            entities['recipient'] = email_match.group() if email_match else "unknown@example.com"
            entities['subject'] = "General Inquiry"
        elif intent == 'weather':
            entities['location'] = "current"
        elif intent == 'set_reminder':
            entities['task'] = text
            entities['time'] = "now"
        
        return entities

# ==========================================
# 5. SPEECH RECOGNITION
# ==========================================
class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def listen(self) -> Optional[str]:
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=10)
            text = self.recognizer.recognize_google(audio, language=Config.LANGUAGE)
            logger.info(f"Recognized: {text}")
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None

# ==========================================
# 6. TASK EXECUTOR
# ==========================================
class TaskExecutor:
    def __init__(self):
        self.weather = WeatherAPI(Config.WEATHER_API_KEY)
        self.email = EmailAPI(Config.EMAIL_API_KEY)
        self.smart_home = SmartHomeAPI(Config.SMART_HOME_API_KEY)
        self.security = SecurityManager(Config.ENCRYPTION_KEY)

    def execute(self, intent: str, entities: Dict) -> str:
        if intent == 'send_email':
            return self.email.send(entities['recipient'], entities['subject'], "Hello")
        elif intent == 'weather':
            return self.weather.get_weather(entities['location'])
        elif intent == 'smart_home':
            return self.smart_home.control("living_room_light", "on")
        elif intent == 'set_reminder':
            return f"Reminder set: {entities['task']}"
        else:
            return "I'm not sure how to handle that."

# ==========================================
# 7. MAIN VOICE ASSISTANT
# ==========================================
class VoiceAssistant:
    def __init__(self):
        self.nlp = NLPEngine()
        self.speech = SpeechRecognizer()
        self.executor = TaskExecutor()
        self.running = True

    def run(self):
        print("Voice Assistant Started. Say 'Hello' to begin.")
        while self.running:
            try:
                text = self.speech.listen()
                if not text:
                    continue
                
                intent, response, entities = self.nlp.classify(text)
                
                if intent == 'custom':
                    print(f"Assistant: {response}")
                else:
                    result = self.executor.execute(intent, entities)
                    print(f"Assistant: {result}")
                    
            except KeyboardInterrupt:
                print("\nStopping Assistant...")
                self.running = False
            except Exception as e:
                logger.error(f"System Error: {e}")
                print("Assistant: An error occurred. Please try again.")

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()