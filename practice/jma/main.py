import requests
import flet

class WeatherApp:
    def __init__(self, master):
        self.master = master
        master.title("天気予報")

        # 地域選択用のドロップダウンメニューを作成
        self.region_label = tk.Label(master, text="地域を選択:")
        self.region_label.pack(pady=10)

        self.region_var = tk.StringVar()
        self.region_dropdown = ttk.Combobox(master, textvariable=self.region_var)
        self.region_dropdown.pack()

        # 地域コードの辞書を作成
        self.region_codes = {
            "北海道地方": "010100",
            "東北地方": "020000",
            "関東地方": "040000",
            "中部地方": "050000",
            "近畿地方": "060000",
            "中国地方": "070000",
            "四国地方": "080000",
            "九州地方": "090000"
        }

        # ドロップダウンメニューにオプションを設定
        self.region_dropdown["values"] = list(self.region_codes.keys())
        self.region_dropdown.current(0)  # 初期値を北海道地方に設定

        # 天気予報を表示するラベルを作成
        self.weather_label = tk.Label(master, text="", font=("Arial", 16))
        self.weather_label.pack(pady=20)

        # 天気予報を取得するボタンを作成
        self.get_forecast_button = tk.Button(master, text="天気予報を取得", command=self.get_weather_forecast)
        self.get_forecast_button.pack(pady=10)

    def get_weather_forecast(self):
        # 選択された地域のエリアコードを取得
        selected_region = self.region_var.get()
        area_code = self.region_codes[selected_region]

        # 気象庁のAPIからデータを取得
        area_url = f"https://www.jma.go.jp/bosai/common/const/area.json"
        forecast_url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

        try:
            # エリア情報を取得
            area_response = requests.get(area_url)
            area_data = area_response.json()

            # 天気予報データを取得
            forecast_response = requests.get(forecast_url)
            forecast_data = forecast_response.json()

            # 天気予報の情報を抽出
            today_weather = forecast_data[0]["timeSeries"][0]["areas"][0]
            weather_text = f"{today_weather['weathers'][0]}\n気温: {today_weather['temps'][0]}°C"

            # 天気予報を表示
            self.weather_label.config(text=weather_text)

        except requests.exceptions.RequestException as e:
            self.weather_label.config(text=f"エラーが発生しました: {e}")

root = tk.Tk()
app = WeatherApp(root)
root.mainloop()