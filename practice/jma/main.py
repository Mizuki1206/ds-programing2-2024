import requests
import flet as ft
import json

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.window_width = 1000
    page.window_height = 600

    def get_area_data():
        """地域データを取得する関数"""
        try:
            response = requests.get('https://www.jma.go.jp/bosai/common/const/area.json')
            return response.json()
        except:
            return {}

    def get_weather_data(area_code):
        """特定地域の天気データを取得する関数"""
        try:
            url = f'https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json'
            response = requests.get(url)
            return response.json()[0]
        except:
            return {}

    def on_area_select(e):
        """地域が選択された時の処理"""
        area_code = e.control.data
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
                                            f"地域: {weather_info['area']['name']}", 
                                            size=20, 
                                            weight=ft.FontWeight.BOLD
                                        ),
                                        ft.Text(
                                            f"天気: {weather_info.get('weathers', ['データなし'])[0]}", 
                                            size=16
                                        ),
                                        ft.Text(
                                            f"気温: {temps[0]}℃", 
                                            size=16
                                        ),
                                    ]
                                ),
                                padding=20
                            )
                        )
                    ]
                )
                page.update()
            except:
                weather_display.content = ft.Text("データの取得に失敗しました")
                page.update()

    def create_area_tree():
        """階層構造のある地域リストを作成"""
        area_data = get_area_data()
        area_tree = ft.ListView(expand=1, spacing=10, padding=20)

        if 'centers' in area_data and 'offices' in area_data:
            # 地方ごとの ExpansionTile を作成
            for center_code, center_info in area_data['centers'].items():
                sub_areas = []
                
                # その地方に属する都道府県を追加
                if 'children' in center_info:
                    for office_code in center_info['children']:
                        if office_code in area_data['offices']:
                            office_info = area_data['offices'][office_code]
                            
                            # さらに細かい地域がある場合
                            sub_regions = []
                            if 'children' in office_info:
                                for child_code in office_info['children']:
                                    # 地域コードから地域名を取得（実際のデータ構造に応じて調整が必要）
                                    sub_regions.append(
                                        ft.TextButton(
                                            text=f"- {child_code}",
                                            data=child_code,
                                            on_click=on_area_select
                                        )
                                    )

                            # 都道府県レベルの ExpansionTile
                            sub_areas.append(
                                ft.ExpansionTile(
                                    title=ft.Text(office_info['name']),
                                    controls=sub_regions
                                )
                            )

                # 地方レベルの ExpansionTile
                area_tree.controls.append(
                    ft.ExpansionTile(
                        title=ft.Text(center_info['name']),
                        controls=sub_areas
                    )
                )

        return area_tree

    # 天気情報表示エリア
    weather_display = ft.Container(
        content=ft.Text("地域を選択してください"),
        expand=True,
        padding=20
    )

    # メインレイアウト
    page.add(
        ft.Row(
            controls=[
                # 左側：階層構造の地域リスト
                ft.Container(
                    content=create_area_tree(),
                    width=300,
                    bgcolor=ft.colors.BLUE_GREY_100,
                ),
                # 右側：天気情報
                weather_display
            ],
            expand=True
        )
    )

ft.app(target=main)