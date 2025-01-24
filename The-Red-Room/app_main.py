import os
import pygame
import requests
import time
import threading
import datetime
import pyttsx3
import subprocess
import queue

# Set environment variable to hide the support prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
pygame.init()

# Initialize Text-to-Speech with Windows Zira
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if "Zira" in voice.name:
        engine.setProperty('voice', voice.id)

# Pygame settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("News and Weather Update")

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Replace with your actual API keys
NEWS_API_KEY = 'Your NewsAPI Key'
WEATHER_API_KEY = 'Your OpenWeatherMap Key'
NEWS_BASE_URL = 'https://newsapi.org/v2/top-headlines'
WEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

# Function to determine greeting based on time
def get_time_greeting():
    current_hour = datetime.datetime.now().hour
    return f"Good {'morning' if current_hour < 12 else 'afternoon' if current_hour < 16 else 'evening'}," 

# Function to get the appropriate suffix for the day
def get_day_suffix(day):
    if 10 <= day % 100 <= 20:
        return "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return suffix

# Function to get the current date
def current_date():
    now = datetime.datetime.now()
    day = now.day
    day_suffix = get_day_suffix(day)
    return now.strftime(f"%A, the {day}{day_suffix} of %B, %Y")

# Function to get the current time
def current_time():
    return datetime.datetime.now().strftime("%I:%M %p")

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_top_headlines():
    params = {
        'apiKey': NEWS_API_KEY,
        'language': 'en',
    }
    response = requests.get(NEWS_BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['articles']
    return []

def get_weather(city='Colombo', country='LK'):
    params = {
        'q': f'{city},{country}',
        'appid': WEATHER_API_KEY,
        'units': 'metric'
    }
    response = requests.get(WEATHER_BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'description': data['weather'][0]['description']
        }
    return None

def draw_text(surface, text, pos, size=24):
    font = pygame.font.SysFont('Arial', size)
    text_surface = font.render(text, True, RED)
    surface.blit(text_surface, pos)

def run_display(weather, articles):
    clock = pygame.time.Clock()
    
    news_update_interval = 1200
    weather_update_interval = 600

    last_news_update = time.time()
    last_weather_update = time.time()
    
    selected_headline_index = 0  # Track which headline is currently selected
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_headline_index = (selected_headline_index + 1) % len(articles)
                elif event.key == pygame.K_UP:
                    selected_headline_index = (selected_headline_index - 1) % len(articles)
                elif event.key == pygame.K_RETURN:
                    if articles:
                        url = articles[selected_headline_index].get('url')
                        if url:
                            subprocess.run(['start', url], shell=True)  # Use 'start' for Windows

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if time.time() - last_news_update > news_update_interval:
            articles = get_top_headlines()
            selected_headline_index = 0  # Reset selection on update
            last_news_update = time.time()
        
        if time.time() - last_weather_update > weather_update_interval:
            weather = get_weather()
            last_weather_update = time.time()

        screen.fill(BLACK)

        draw_text(screen, f"Current Date & Time: {now}", (10, 10))

        if weather:
            draw_text(screen, f"Weather in Colombo:", (10, 50))
            draw_text(screen, f"Temperature: {weather['temperature']}°C", (10, 80))
            draw_text(screen, f"Humidity: {weather['humidity']}%", (10, 110))
            draw_text(screen, f"Pressure: {weather['pressure']} hPa", (10, 140))
            draw_text(screen, f"Description: {weather['description']}", (10, 170))
        
        # Draw news headlines
        draw_text(screen, "Top World Headlines:", (10, 210))
        displayed_headlines = 0
        for index, article in enumerate(articles):
            if 'title' in article and displayed_headlines < 20:
                headline_text = f"{displayed_headlines + 1}. {article['title']}"
                text_surface = pygame.font.SysFont('Arial', 24).render(headline_text, True, (255, 255, 255))
                
                if index == selected_headline_index:
                    highlight_rect = text_surface.get_rect(topleft=(10, 240 + displayed_headlines * 30))
                    pygame.draw.rect(screen, (128, 128, 128), highlight_rect)
                    screen.blit(text_surface, highlight_rect.topleft)
                else:
                    draw_text(screen, headline_text, (10, 240 + displayed_headlines * 30))

                displayed_headlines += 1

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def main():

     # Start the other scripts
     # other_scripts_path = ["monitorV5.py"]  # List of scripts to run
     # for script in other_scripts_path:
         # subprocess.Popen(['python', script])  # Run each script in the background
    
    greeting = get_time_greeting()
    date = current_date()
    current_time_str = current_time()

    # Fetch the weather information
    weather = get_weather()
    
    # Initialize temperature, humidity, pressure, and description
    temperature = humidity = pressure = weather_description = "N/A"
    
    if weather:
        temperature = weather['temperature']
        humidity = weather['humidity']
        pressure = weather['pressure']
        weather_description = weather['description']

    response_text = (f"{greeting} the current date and time in Colombo, Sri Lanka, is {date}, {current_time_str}. "
                     f"The temperature is {temperature} degrees Celsius, with a humidity of {humidity}%, "
                     f"an atmospheric pressure of {pressure} hPa, and with {weather_description}.")

    # Start the speaking in a separate thread
    threading.Thread(target=speak, args=(response_text,)).start()

    # Run the Pygame display loop
    run_display(weather, get_top_headlines())

if __name__ == '__main__':
    main()
