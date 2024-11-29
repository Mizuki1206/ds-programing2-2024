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

    try:
        with open(AREAS_JSON_PATH, 'r', encoding='utf-8') as f:
            areas_data = json.load(f)

        def create_navigation_items():
            navigation_items = []
            
            # 地方（centers）のループ
            for center_code, center_info in areas_data['centers'].items():
                center_children = []
                
                # 各地方の子要素（offices）を処理
                for office_code in center_info['children']:
                    if office_code in areas_data['offices']:
                        office_info = areas_data['offices'][office_code]
                        
                        # class10sの情報を取得
                        class10_children = []
                        for class10_code in office_info['children']:
                            if class10_code in areas_data['class10s']:
                                class10_info = areas_data['class10s'][class10_code]
                                class10_children.append(
                                    ft.NavigationRailDestination(
                                        icon=ft.icons.LOCATION_ON_OUTLINED,
                                        selected_icon=ft.icons.LOCATION_ON,
                                        label=class10_info['name'],
                                        data=class10_code
                                    )
                                )
                        
                        # officesレベルのナビゲーションアイテム
                        center_children.append(
                            ft.ExpansionTile(
                                title=ft.Text(office_info['name']),
                                subtitle=ft.Text(office_info['officeName']),
                                children=class10_children
                            )
                        )

                # centersレベルのナビゲーションアイテム
                navigation_items.append(
                    ft.ExpansionTile(
                        title=ft.Text(center_info['name']),
                        subtitle=ft.Text(center_info['officeName']),
                        children=center_children
                    )
                )
            
            return navigation_items

        # ナビゲーションパネルの作成
        navigation_panel = ft.Column(
            controls=create_navigation_items(),
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    except Exception as e:
        print(f"Error loading areas data: {e}")
        navigation_panel = ft.Column([
            ft.Text("データの読み込みに失敗しました")
        ])

    # メインレイアウト
    page.add(
        ft.Row([
            ft.Container(
                content=navigation_panel,
                width=300,
                border=ft.border.all(1, ft.colors.OUTLINE),
            ),
            ft.VerticalDivider(width=1),
            weather_container
        ], expand=True)
    )