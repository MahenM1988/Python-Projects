import os
import subprocess
import pygame
import datetime
import speech_recognition as sr
import pyttsx3
import requests
import platform
import psutil
import GPUtil
import webbrowser
import configparser
import threading
from geopy.geocoders import Nominatim

# Set environment variable to hide the support prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
pygame.init()

# Initialize Text-to-Speech with Windows Zira
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if "Zira" in voice.name:
        engine.setProperty('voice', voice.id)

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Replace with your actual API keys and URLs from config
NEWS_API_KEY = config['API']['NEWS_API_KEY']
WEATHER_API_KEY = config['API']['WEATHER_API_KEY']
NEWS_BASE_URL = config['API']['NEWS_BASE_URL']
WEATHER_BASE_URL = config['API']['WEATHER_BASE_URL']

# Get directory from config
directory_to_check = config['Settings']['DIRECTORY']

# Flag to control TTS
is_tts_running = False

def speak(text):
    global is_tts_running
    is_tts_running = True
    engine.say(text)
    engine.runAndWait()
    is_tts_running = False

def stop_tts_on_space():
    global is_tts_running
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and is_tts_running:
                engine.stop()
                is_tts_running = False
                print("TTS stopped.")

# Start the key press listener in a separate thread
threading.Thread(target=stop_tts_on_space, daemon=True).start()

def get_time_greeting():
    current_hour = datetime.datetime.now().hour
    return f"Good {'morning' if current_hour < 12 else 'afternoon' if current_hour < 16 else 'evening'},"


def get_day_suffix(day):
    if 10 <= day % 100 <= 20:
        return "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return suffix


def current_date():
    now = datetime.datetime.now()
    day = now.day
    day_suffix = get_day_suffix(day)
    return now.strftime(f"%A, the {day}{day_suffix} of %B, %Y")


def current_time():
    return datetime.datetime.now().strftime("%I:%M %p")


def get_top_headlines():
    params = {
        'apiKey': NEWS_API_KEY,
        'language': 'en',
    }
    try:
        response = requests.get(NEWS_BASE_URL, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        news_headlines = response.json()['articles']
        return news_headlines
    except requests.RequestException as e:
        print(f"Error fetching news: {e}")
        return []


def get_city_from_ip():
    try:
        # Use an IP to location API to get the city and country based on the local IP
        ip_info = requests.get('http://ip-api.com/json')
        ip_info.raise_for_status()
        ip_data = ip_info.json()
        
        city = ip_data.get('city', 'Unknown')
        country = ip_data.get('country', 'Unknown')
        
        return city, country
    except requests.RequestException as e:
        print(f"Error fetching location based on IP: {e}")
        return 'Unknown', 'Unknown'


def get_weather():
    # Get city and country from IP
    city, country = get_city_from_ip()
    
    params = {
        'q': f'{city},{country}',
        'appid': WEATHER_API_KEY,
        'units': 'metric'
    }
    
    try:
        response = requests.get(WEATHER_BASE_URL, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        
        return {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'description': data['weather'][0]['description']
        }
    except requests.RequestException as e:
        print(f"Error fetching weather: {e}")
        return None


def report_weather(speak_function):
    weather = get_weather()
    if weather:
        temperature = weather['temperature']
        humidity = weather['humidity']
        pressure = weather['pressure']
        weather_description = weather['description']
        
        response_text = (f"The temperature is {temperature} degrees Celsius, "
                         f"with a humidity of {humidity}%, an atmospheric pressure of {pressure} hPa, "
                         f"and {weather_description}.")
        print(response_text)
        speak_function(response_text)  # Pass the speak function as an argument
    else:
        print("Could not fetch weather data.")


def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            return "Sorry, I did not understand that."
        except sr.RequestError:
            return "Could not request results."


def handle_command(user_input, directory):
    if "access entertainment library" in user_input.lower():
        load_entertainment_library(directory)
    elif "current date and time" in user_input.lower():
        report_current_datetime()
    elif "current weather update" in user_input.lower():
        report_weather(speak)
    elif "news headlines" in user_input.lower():
        fetch_news_headlines()
    elif "search" in user_input.lower():
        perform_search(user_input)
    elif "look up" in user_input.lower():
        look_up(user_input)
    elif "system specifications" in user_input.lower():
        report_system_specs()
    else:
        print(f"User input: {user_input}")


def main():
    use_console = input("Would you like to use the console (C) or speech recognition (S)? ").strip().upper()

    # Get city and country from IP for accurate location info
    city, country = get_city_from_ip()

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

    # Now that city and country are defined, we can include them in the response text
    response_text = (f"{greeting} the current date and time in {city}, {country} is {date}, {current_time_str}. "
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
