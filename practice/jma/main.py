import flet as ft
import requests

def get_area_data():
    url = "https://www.jma.go.jp/bosai/common/const/area.json"
    return requests.get(url).json()

def get_weather_data(area_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    return requests.get(url).json()

def main(page: ft.Page):
    page.title = "天気予報"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    weather_view = ft.Container(
        content=ft.Text("Active view", color="white"),
        alignment=ft.alignment.center,
        bgcolor=ft.colors.SURFACE_VARIANT,
        expand=True,
    )

    def weather(e, area_code):
        try:
            weather_data = get_weather_data(area_code)
            weather_info = weather_data[0]["timeSeries"][0]["areas"][0]
            weather = weather_info["weather"]
            weather_view.content = ft.Text(f"天気: {weather}", color="white")
            page.update()
        except Exception as e:
            weather_view.content = ft.Text(f"エラーが発生しました:{str(e)}", color="white")
            page.update()

    area_data = get_area_data()
    centers = area_data["centers"]

    # 地域メニューの作成
    region_menu = ft.Column(
        controls=[
            ft.Container(
                content=ft.Text("地域を選択", color="white"),
                padding=10,
            )
        ],
        scroll=ft.ScrollMode.AUTO,
    )

    # 各地域のボタンを作成
    for code, region in centers.items():
        region_menu.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(region["name"], color="white", size=14),
                    ft.Text(code, color="white", size=12, opacity=0.5)
                ]),
                padding=10,
                margin=ft.margin.only(bottom=5),
                ink=True,
                on_click=lambda e, code=code: weather(e, code),
            )
        )

    # レイアウトの設定
    page.add(
        ft.Row(
            [
                ft.Container(
                    content=region_menu,
                    width=200,
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border=ft.border.only(right=ft.border.BorderSide(1, ft.colors.OUTLINE)),
                ),
                weather_view,
            ],
            expand=True,
        )
    )

ft.app(main)