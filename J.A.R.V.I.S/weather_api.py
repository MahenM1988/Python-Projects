import configparser
import requests

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

WEATHER_BASE_URL = config['API']['WEATHER_BASE_URL']
WEATHER_API_KEY = config['API']['WEATHER_API_KEY']

def get_weather(city='Colombo', country='LK'):
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
                         f"with a humidity of {humidity}%, "
                         f"an atmospheric pressure of {pressure} hPa, "
                         f"and {weather_description}.")
        print(response_text)
        speak_function(response_text)  # Pass the speak function as an argument
    else:
        print("Could not fetch weather data.")
