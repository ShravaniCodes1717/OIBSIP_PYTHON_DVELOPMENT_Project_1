import speech_recognition as sr
import pyttsx3
import datetime
import googlesearch as google_search

# Initialize TTS Engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) # Set voice

def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            print(f"User: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            return "no_input"
        except sr.UnknownValueError:
            return "unknown"

def main():
    speak("Hello! I am your assistant. How can I help?")
    
    while True:
        command = listen()
        
        if command == "no_input":
            continue
        
        if "hello" in command:
            speak("Hello there! How are you today?")
        
        elif "time" in command:
            now = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The current time is {now}")
        
        elif "date" in command:
            today = datetime.datetime.now().strftime("%B %d, %Y")
            speak(f"Today is {today}")
        
        elif "search" in command:
            # Extract query after 'search'
            query = command.replace("search", "").strip()
            speak(f"Searching the web for {query}")
            try:
                # Perform search (prints to console, could be enhanced to read results)
                for url in google_search.search(query, num_results=1):
                    speak(f"Here is a result: {url}")
                    break
            except Exception as e:
                speak("I couldn't find anything.")
        
        elif "exit" in command:
            speak("Goodbye!")
            break

if __name__ == "__main__":
    main()