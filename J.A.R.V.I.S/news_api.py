import configparser
import requests

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

NEWS_BASE_URL = config['API']['NEWS_BASE_URL']
NEWS_API_KEY = config['API']['NEWS_API_KEY']

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

def fetch_news_headlines(speak_function):
    news_headlines = get_top_headlines()
    if news_headlines:
        headlines_text = "In the World News Today:\n"
        for index, article in enumerate(news_headlines[:10], start=1):  # Start numbering from 1
            headlines_text += f"{index}. {article['title']}\n"
        print(headlines_text)
        speak_function("Fetching the top news headlines now")  
    else:
        print("Unable to fetch news headlines at the moment.")


