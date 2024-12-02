import requests
import flet as ft
import json

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.window_width = 1000
    page.window_height = 600

    def get_area_data():
        try:
            response = requests.get('https://www.jma.go.jp/bosai/common/const/area.json')
            return response.json()
        except:
            return {}

    def get_weather_data(area_code):
        try:
            url = f'https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json'
            response = requests.get(url)
            return response.json()[0]
        except:
            return {}

    def on_area_select(e):
        area_code = e.control.data
        area_name = e.control.text  # ボタンのテキスト（地域名）を取得
        weather_data = get_weather_data(area_code)
        
        if weather_data:
            try:
                weather_info = weather_data['timeSeries'][0]['areas'][0]
                temps = weather_data['timeSeries'][2]['areas'][0]['temps']
                
                weather_display.content = ft.Column(
                    controls=[
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            f"地域: {area_name}", 
                                            size=20, 
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.colors.BLACK
                                        ),
                                        ft.Text(
                                            f"天気: {weather_info.get('weathers', ['データなし'])[0]}", 
                                            size=16,
                                            color=ft.colors.BLACK
                                        ),
                                        ft.Text(
                                            f"気温: {temps[0]}℃", 
                                            size=16,
                                            color=ft.colors.BLACK
                                        ),
                                    ]
                                ),
                                padding=20,
                                bgcolor=ft.colors.WHITE
                            )
                        )
                    ]
                )
                page.update()
            except:
                weather_display.content = ft.Text("データの取得に失敗しました")
                page.update()

    def create_area_tree():
        area_data = get_area_data()
        area_tree = ft.ListView(expand=1, spacing=10, padding=20)

        # 地域名とコードのマッピングを作成
        area_names = {}
        if 'offices' in area_data:
            for code, info in area_data['offices'].items():
                area_names[code] = info['name']

        if 'centers' in area_data and 'offices' in area_data:
            for center_code, center_info in area_data['centers'].items():
                sub_areas = []
                
                if 'children' in center_info:
                    for office_code in center_info['children']:
                        if office_code in area_data['offices']:
                            office_info = area_data['offices'][office_code]
                            
                            if 'children' in office_info:
                                for child_code in office_info['children']:
                                    # 地域名を取得（存在しない場合はコードを使用）
                                    area_name = area_names.get(child_code, child_code)
                                    sub_areas.append(
                                        ft.TextButton(
                                            text=area_name,  # 地域名を表示
                                            data=child_code,  # コードはデータとして保持
                                            on_click=on_area_select,
                                            style=ft.ButtonStyle(
                                                color=ft.colors.WHITE,
                                                padding=10,
                                            )
                                        )
                                    )

                # 地方レベルの ExpansionTile
                area_tree.controls.append(
                    ft.ExpansionTile(
                        title=ft.Text(
                            center_info['name'],
                            color=ft.colors.WHITE,
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                        controls=sub_areas,
                        bgcolor=ft.colors.BLUE_GREY_700,
                    )
                )

        return area_tree

    # 天気情報表示エリア
    weather_display = ft.Container(
        content=ft.Text(
            "地域を選択してください",
            color=ft.colors.BLACK,
            size=16
        ),
        expand=True,
        padding=20,
        bgcolor=ft.colors.WHITE
    )

    # メインレイアウト
    page.add(
        ft.Row(
            controls=[
                ft.Container(
                    content=create_area_tree(),
                    width=300,
                    bgcolor=ft.colors.BLUE_GREY_900,
                ),
                weather_display
            ],
            expand=True
        )
    )

    page.bgcolor = ft.colors.WHITE
    page.update()

ft.app(target=main)