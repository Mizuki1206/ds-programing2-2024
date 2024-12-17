import requests
import json
from database.models import WeatherData

def fetch_weather_data(area_code):
    url = f'https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def update_weather_data(conn, area_code):
    data = fetch_weather_data(area_code)
    if data:
        weather_data = WeatherData(conn)
        weather_data.save_forecast(data, area_code)
        return True
    return False