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

def main(page: ft.Page):
    page.title = "天気予報アプリ"

    area_dara = get_area_data()
    

    rail = ft.NavigationRail(
        selected_index = 0,
        label_type = ft.NavigationRailLabelType.All,
        extended = True,
        destinations = [
            ft.NavigationRailDestination(
                icon = ft.icons.FAVORITE_BORDER,
                selected_icon = ft.icons.FAVORITE,
                label = "地域を選択"
            ),
        ]
    )

    area_list = 



ft.app(main)
