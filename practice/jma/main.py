import flet as ft
import requests


def main(page: ft.Page):
    page.title = "天気予報アプリ"

def get_area_data():
    url = "https://www.jma.go.jp/bosai/common/const/area.json"
    return requests.get(url).json()

def get_weather_data(area_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    return requests.get(url).json()


ft.app(main)
