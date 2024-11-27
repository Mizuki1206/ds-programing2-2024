import flet as ft
import requests

def get_area_data():
    url = "https://www.jma.go.jp/bosai/common/const/area.json"
    return requests.get(url).json()

def get_weather_data(area_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    return requests.get(url).json()

def main(page: ft.Page):
    page.title = "天気予報アプリ"

    weather_text = ft.Text()

    def weather(e, area_code):
        try:
            weather_data = get_weather_data(area_code)
            weather_info = weather_data[0]["timeSeries"][0]["areas"][0]
            weather = weather_info["weather"]
            weather_text.value = f"天気: {weather}"
        except:
            weather_text.value = f"エラーが発生しました:{str(e)}"

    area_data = get_area_data()
    centers = area_data["centers"]

    area_Dropdown = ft.Dropdown(
        width = 400,
        options = [
            ft.dropdown.Option(key = code, text = region["name"])
            for code, region in centers.items()
        ]
    )

    weather_button = ft.ElevatedButton(
        text = "天気を表示",
        on_click = lambda e: weather(e, area_Dropdown.value)
    )

    page.add(
        ft.Column([
            ft.Text("地域を選択してください", size = 20),
            area_Dropdown,
            weather_button,
            weather_text
        ])
    )



ft.app(main)