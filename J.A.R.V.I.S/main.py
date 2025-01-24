import os
import configparser
import pygame
import speech_recognition as sr
import pyttsx3
import threading
import webbrowser
from weather_api import get_weather, report_weather  # type: ignore 
from news_api import fetch_news_headlines  # type: ignore 
from sys_info import get_system_info  # type: ignore
from date_time import current_date, current_time # type: ignore
from greeting import get_time_greeting # type: ignore

# Set environment variable to hide the support prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
pygame.init()

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Get directory from config
directory_to_check = config['Settings']['DIRECTORY']

# Initialize Text-to-Speech with Windows Zira
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if "Zira" in voice.name:
        engine.setProperty('voice', voice.id)

# Flag to control TTS
tts_running = False

def speak():
    global tts_running
    tts_running = True
    engine.say()
    engine.runAndWait()
    tts_running = False

def stop_tts_on_space():
    global tts_running
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and tts_running:
                    engine.stop()
                    tts_running = False
                    print("TTS stopped.")

# Start the key press listener in a separate thread
threading.Thread(target=stop_tts_on_space, daemon=True).start()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Waiting for command...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"User command: {command}")
            return command
        except sr.UnknownValueError:
            return "Command not recognized."
        except sr.RequestError:
            return "Could not process command."
        
def list_files_and_folders(directory):
    try:
        items = os.listdir(directory)
        # Separate folders and files
        folders = [os.path.join(directory, item) for item in items if os.path.isdir(os.path.join(directory, item))]
        files = [os.path.join(directory, item) for item in items if os.path.isfile(os.path.join(directory, item))]
        return sorted(folders) + sorted(files)  # Sort folders and files separately
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def play_file(file_path):
    try:
        if file_path.lower().endswith(('.mp4', '.mp3', '.wav', '.avi', '.mkv', '.wmv')):
            os.startfile(file_path)
            print(f"Playing: {file_path}")
        else:
            print(f"Unsupported file type: {file_path}")
    except Exception as e:
        print(f"Failed to play {file_path}: {str(e)}")

def access_main_server(start_directory):
    current_directory = start_directory
    print("Accessing Main Server...")
    
    while True:
        items = list_files_and_folders(current_directory)
        print("\nFiles and Folders:")
        for item in items:
            print(f"- {os.path.basename(item)}")

        print("\nType a file or folder name to select it, 'up' to go up a directory, 'play [file name]' to play, or 'exit' to leave:")
        
        command = input("Your command: ").strip()
        
        if command.lower() == "exit":
            break
        elif command.lower() == "up":
            current_directory = os.path.dirname(current_directory)
            print(f"Going up to: {current_directory}")
        elif command.lower().startswith("play "):
            file_name = command[5:].strip()  # Get the name after "play "
            file_path = os.path.join(current_directory, file_name)
            if os.path.isfile(file_path):
                play_file(file_path)
            else:
                print(f"File not found: {file_name}")
        else:
            selected_item = None
            for item in items:
                if os.path.basename(item).lower() == command.lower():
                    selected_item = item
                    break
            
            if selected_item:
                if os.path.isdir(selected_item):
                    current_directory = selected_item
                elif os.path.isfile(selected_item):
                    play_file(selected_item)
                else:
                    print(f"Unknown item: {selected_item}")
            else:
                print("No matching file or folder found. Please try again.")

def report_current_datetime():
    date = current_date()
    current_time_str = current_time()
    response_text = (f"The current date and time in Colombo, Sri Lanka, is {date}, {current_time_str}.")
    print(response_text)
    speak(response_text)

def report_system_specs():
    processor, motherboard, ram_total, disk_total, gpu_name, os_info = get_system_info()
    sys_info_text = (f"I am currently running on an {processor}. The motherboard is {motherboard}. "
                     f"The GPU is {gpu_name}. There is {ram_total:.2f} GB RAM installed, "
                     f"and the total disk space is {disk_total:.2f} GB. The operating system is {os_info}.")
    print(sys_info_text)
    speak(sys_info_text)

def perform_search(user_input):
    user_input_lower = user_input.lower()  # Convert input to lower case
    parts = user_input_lower.split("search", 1)
    if len(parts) > 1:
        query = parts[1].strip()
        webbrowser.open(f"https://www.duckduckgo.com/{query}")
        speak(f"Searching for {query}")
    else:
        print("No search query entered.")

def look_up(user_input):
    user_input_lower = user_input.lower()  # Convert input to lower case
    parts = user_input_lower.split("look up", 1)
    if len(parts) > 1:
        query = parts[1].strip()
        webbrowser.open(f"https://en.wikipedia.org/wiki/{query}")
        speak(f"Looking up: {query}")
    else:
        print("Nothing to look up.")

def handle_command(user_input, directory):
    user_input_lower = user_input.lower()
    
    if "access main server" in user_input_lower:
        speak("Accessing Main Server...")
        access_main_server(directory)
    elif "current date and time" in user_input_lower:
        report_current_datetime()
    elif "current weather update" in user_input_lower:
        report_weather(speak)
    elif "news headlines" in user_input_lower:
        fetch_news_headlines(speak)
    elif "search" in user_input.lower():
        perform_search(user_input)
    elif "look up" in user_input.lower():
        look_up(user_input)
    elif "system information" in user_input_lower:
        report_system_specs()
    else:
        speak("Command not recognized.")
        print(f"User command: {user_input}")

def main():
    use_console = input("Would you like to use the console (C) or speech recognition (S)? ").strip().upper()

    greeting = get_time_greeting()
    date = current_date()
    current_time_str = current_time()

    # Initial response with weather update
    weather = get_weather()
    temperature = humidity = pressure = weather_description = "N/A"
    
    if weather:
        temperature = weather['temperature']
        humidity = weather['humidity']
        pressure = weather['pressure']
        weather_description = weather['description']

    response_text = (f"{greeting} the current date and time in Colombo, Sri Lanka, is {date}, {current_time_str}. "
                     f"The temperature is {temperature} degrees Celsius, with a humidity of {humidity}%, "
                     f"an atmospheric pressure of {pressure} hPa, and with {weather_description}.")
    
    print(response_text)
    speak(response_text)

    # Conversation loop
    while True:
        if use_console == "C":
            user_input = input("You: ")
        elif use_console == "S":
            user_input = recognize_speech()
        
        if user_input.lower() == "exit":
            confirm_exit = input("Are you sure you want to exit? (yes/no): ").strip().lower()
            if confirm_exit == "yes":
                break
        
        handle_command(user_input, directory_to_check)

if __name__ == "__main__":
    main()