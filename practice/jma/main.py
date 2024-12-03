import requests
import flet as ft
import json
from datetime import datetime

def main(page: ft.Page):
    # ページの基本設定
    page.title = "天気予報アプリ"
    page.bgcolor = "#E8E8E8"  # 背景色をグレーに
    page.padding = 0  # パディングを0に

    def fetch_area_data():
        try:
            response = requests.get("https://www.jma.go.jp/bosai/common/const/area.json")
            return response.json()
        except:
            return None

    def fetch_weather_data(area_code):
        try:
            response = requests.get(f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json")
            return response.json()
        except:
            return None

    def format_datetime(datetime_str):
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime('%Y年%m月%d日 %H時%M分')

    def get_weather_emoji(weather):
        weather_emojis = {
            "晴れ": "☀️",
            "晴": "☀️",
            "曇り": "☁️",
            "曇": "☁️",
            "雨": "🌧️",
            "雪": "❄️",
            "晴時々曇": "🌤️",
            "晴一時雨": "🌦️",
            "晴時々雨": "🌦️",
            "曇時々晴": "⛅",
            "曇一時雨": "🌧️",
            "晴のち曇": "🌥️",
            "晴のち雨": "🌦️",
            "曇のち雨": "🌧️",
            "雨のち曇": "🌥️",
        }
        # 部分一致で検索
        for key in weather_emojis:
            if key in weather:
                return weather_emojis[key]
        return "🌈"

    def create_weather_card(date, weather, temp_min, temp_max):
        weather_emoji = get_weather_emoji(weather)
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(date, size=16, weight=ft.FontWeight.BOLD, color="black"),
                    ft.Text(weather_emoji, size=30),  # 絵文字を追加
                    ft.Text(weather, size=20, color="black"),
                    ft.Row(
                        controls=[
                            ft.Text(f"{temp_min}°C", size=16, color="blue"),
                            ft.Text(" / ", size=16, color="black"),
                            ft.Text(f"{temp_max}°C", size=16, color="red"),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            bgcolor="white",
            border_radius=10,
            width=200,
        )

    def format_weather_info(weather_data):
        if not weather_data:
            return ft.Text("天気情報を取得できませんでした。")

        try:
            weather_info = weather_data[0]
            weather_cards = ft.Row(controls=[], wrap=True, spacing=10)

            # 基本情報の表示
            basic_info = ft.Text(
                f"""発表元: {weather_info['publishingOffice']}
発表時刻: {format_datetime(weather_info['reportDatetime'])}
地域: {weather_info['timeSeries'][0]['areas'][0]['area']['name']}""",
                size=16,
                weight=ft.FontWeight.NORMAL,
                color="black"
            )

        # 一週間分の天気予報カードを作成
            for i in range(len(weather_info['timeSeries'][0]['timeDefines'])):
                try:
                    date = datetime.fromisoformat(weather_info['timeSeries'][0]['timeDefines'][i].replace('Z', '+00:00')).strftime('%m/%d')
                    weather = weather_info['timeSeries'][0]['areas'][0]['weathers'][i]
                    
                    # 気温情報の取得（利用可能な場合）
                    temp_min = "--"
                    temp_max = "--"
                    if len(weather_info['timeSeries']) > 2:
                        temps = weather_info['timeSeries'][2]['areas'][0].get('temps', [])
                        if len(temps) > i*2+1:
                            temp_min = temps[i*2]
                            temp_max = temps[i*2+1]

                    card = create_weather_card(date, weather, temp_min, temp_max)
                    weather_cards.controls.append(card)
                except Exception as e:
                    print(f"カード作成エラー: {str(e)}")

            # 情報をColumnで縦に並べて返す
            return ft.Column(
                controls=[
                    basic_info,
                    weather_cards
                ],
                scroll=ft.ScrollMode.AUTO
            )

        except Exception as e:
            return ft.Text(f"天気情報の解析中にエラーが発生しました: {str(e)}")

    def on_region_selected(e):
        selected_center = region_dropdown.value
        if selected_center:
            prefecture_options = []
            for office_code, office_info in area_data['offices'].items():
                if office_code.endswith('000'):
                    parent_center = office_info.get('parent')
                    if parent_center == selected_center:
                        prefecture_options.append(
                            ft.dropdown.Option(
                                key=office_code,
                                text=office_info['name']
                            )
                        )
            prefecture_dropdown.options = prefecture_options
            prefecture_dropdown.value = None
            weather_text.content = None
            page.update()

    def on_prefecture_selected(e):
        selected_code = prefecture_dropdown.value
        if selected_code:
            weather_data = fetch_weather_data(selected_code)
            weather_text.content = format_weather_info(weather_data)
            page.update()

    # 地域データの取得と選択肢の作成
    area_data = fetch_area_data()
    region_options = []
    if area_data and 'centers' in area_data:
        for center_code, center_info in area_data['centers'].items():
            region_options.append(
                ft.dropdown.Option(
                    key=center_code,
                    text=center_info['name']
                )
            )

    # ドロップダウンの作成
    region_dropdown = ft.Dropdown(
        label="地方を選択",
        options=region_options,
        on_change=on_region_selected,
        width=250,
        bgcolor="white",
        border_color="transparent",
        text_style=ft.TextStyle(color="black"),
        label_style=ft.TextStyle(color="black")
    )

    prefecture_dropdown = ft.Dropdown(
        label="県を選択",
        options=[],
        on_change=on_prefecture_selected,
        width=250,
        bgcolor="white",
        border_color="transparent",
        text_style=ft.TextStyle(color="black"),
        label_style=ft.TextStyle(color="black")
    )

    weather_text = ft.Container(
        content=None,
        expand=True
    )

    # ヘッダーの作成
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(name=ft.icons.WB_SUNNY, color="white", size=30),
                ft.Text("天気予報", color="white", size=24, weight=ft.FontWeight.BOLD),
            ],
            spacing=10
        ),
        padding=ft.padding.only(left=20, right=20, top=10, bottom=10),
        bgcolor="#3F51B5",
        width=page.window_width
    )

    # 左側のパネル
    left_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column([
                        region_dropdown,
                        prefecture_dropdown
                    ]),
                    padding=20,
                ),
            ],
        ),
        width=300,
        bgcolor="#9EA7BE",
        height=page.window_height
    )

    # メインコンテンツエリア
    main_content = ft.Container(
        content=weather_text,
        expand=True,
        padding=20,
        bgcolor="#E8E8E8"
    )

    # レイアウトの構成
    page.add(
        header,
        ft.Row(
            controls=[
                left_panel,
                main_content
            ],
            expand=True,
        )
    )

    # ウィンドウサイズ変更時の処理
    def on_resize(e):
        header.width = page.window_width
        page.update()

    page.on_resize = on_resize

ft.app(target=main)