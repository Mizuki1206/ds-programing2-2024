import flet as ft
import json
from datetime import datetime

class WeatherApp:
    def __init__(self):
        self.area_data = None
        self.current_weather_data = None
        self.load_data()

    def load_data(self):
        # 地域データの読み込み
        try:
            with open('areas.json', 'r', encoding='utf-8') as f:
                self.area_data = json.load(f)
        except Exception as e:
            print(f"Error loading area data: {e}")
            self.area_data = {}

    def get_weather_data(self, area_code):
        # 天気データの読み込み
        try:
            with open('forecast.json', 'r', encoding='utf-8') as f:
                self.current_weather_data = json.load(f)
            return self.current_weather_data
        except Exception as e:
            print(f"Error loading weather data: {e}")
            return None

def format_date(date_str):
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    return dt.strftime('%m/%d')

def get_weather_icon(weather_code):
    weather_icons = {
        "100": "☀️",  # 晴れ
        "101": "🌤️",  # 晴れ時々曇り
        "200": "☁️",  # くもり
        "201": "⛅",  # くもり時々晴れ
        "202": "🌥️",  # くもり一時晴れ
        "300": "🌧️",  # 雨
        "301": "🌦️",  # 雨時々晴れ
        "302": "🌧️",  # 雨一時晴れ
        "400": "🌨️",  # 雪
    }
    return weather_icons.get(weather_code[:3], "❓")

class WeatherView(ft.UserControl):
    def __init__(self, weather_data):
        super().__init__()
        self.weather_data = weather_data

    def build(self):
        if not self.weather_data:
            return ft.Text("天気データを取得できません")

        # 天気予報データの取得
        time_series = self.weather_data[0]['timeSeries']
        weather_info = time_series[0]  # 天気情報
        temp_info = time_series[2]     # 気温情報

        # 天気予報カードの作成
        weather_cards = []
        for i, date in enumerate(weather_info['timeDefines']):
            area_info = weather_info['areas'][0]  # 最初のエリアのデータを使用
            weather_code = area_info['weatherCodes'][i]
            weather_desc = area_info['weathers'][i]

            # 気温データの取得
            temp = "-- ℃"
            if i < len(temp_info['areas'][0]['temps']):
                temp = f"{temp_info['areas'][0]['temps'][i]} ℃"

            card = ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text(format_date(date), size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(get_weather_icon(weather_code), size=32),
                        ft.Text(weather_desc, size=14, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"気温: {temp}", size=14),
                    ], 
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                )
            )
            weather_cards.append(card)

        return ft.Column([
            ft.Text(
                f"地域: {weather_info['areas'][0]['area']['name']}",
                size=20,
                weight=ft.FontWeight.BOLD
            ),
            ft.Row(
                controls=weather_cards,
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
            )
        ])

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    weather_app = WeatherApp()

    # 天気表示用のコンテナ
    weather_container = ft.Container(
        content=ft.Text("地域を選択してください"),
        expand=True
    )

    def on_region_select(e):
        # 地域が選択されたときの処理
        region_code = e.control.data
        weather_data = weather_app.get_weather_data(region_code)
        
        # 天気表示を更新
        weather_container.content = WeatherView(weather_data)
        page.update()

    # ナビゲーションレール
    rail = ft.NavigationRail(
        selected_index=None,
        label_type=ft.NavigationRailLabelType.ALL,
        extended=True,
        min_width=100,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.LOCATION_ON_OUTLINED,
                selected_icon=ft.icons.LOCATION_ON,
                label="広島県",  # 地域名を直接指定
                data="340000"    # 地域コードを直接指定
            )
        ],
        on_change=on_region_select
    )

    # メインレイアウト
    page.add(
        ft.Row([
            rail,
            ft.VerticalDivider(width=1),
            weather_container
        ], expand=True)
    )

if __name__ == '__main__':
    ft.app(target=main)