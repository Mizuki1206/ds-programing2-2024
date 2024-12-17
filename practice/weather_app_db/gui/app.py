import tkinter as tk
from tkinter import ttk
from datetime import datetime
import sqlite3

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("天気予報アプリ")
        self.root.geometry("800x600")
        
        # データベース接続
        self.conn = sqlite3.connect('weather_app.db')
        self.cursor = self.conn.cursor()
        
        self.create_widgets()
    
    def create_widgets(self):
        # エリア選択フレーム
        self.area_frame = ttk.LabelFrame(self.root, text="エリア選択", padding=10)
        self.area_frame.pack(fill="x", padx=10, pady=5)
        
        # 都道府県選択
        ttk.Label(self.area_frame, text="都道府県:").pack(side="left")
        self.prefecture_var = tk.StringVar()
        self.prefecture_combo = ttk.Combobox(
            self.area_frame, 
            textvariable=self.prefecture_var,
            state='readonly'
        )
        self.prefecture_combo.pack(side="left", padx=5)
        
        # 市区町村選択
        ttk.Label(self.area_frame, text="市区町村:").pack(side="left")
        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(
            self.area_frame, 
            textvariable=self.city_var,
            state='readonly'
        )
        self.city_combo.pack(side="left", padx=5)
        
        # 更新ボタン
        self.update_button = ttk.Button(
            self.area_frame,
            text="更新",
            command=self.update_weather
        )
        self.update_button.pack(side="left", padx=10)
        
        # 天気情報表示フレーム
        self.weather_frame = ttk.LabelFrame(self.root, text="天気情報", padding=10)
        self.weather_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 天気情報を表示するTreeview
        columns = ("日付", "天気", "最高気温", "最低気温", "降水確率")
        self.weather_tree = ttk.Treeview(
            self.weather_frame, 
            columns=columns, 
            show='headings'
        )
        
        # 列の設定
        for col in columns:
            self.weather_tree.heading(col, text=col)
            self.weather_tree.column(col, width=100)
        
        # スクロールバーの追加
        scrollbar = ttk.Scrollbar(
            self.weather_frame,
            orient="vertical",
            command=self.weather_tree.yview
        )
        self.weather_tree.configure(yscrollcommand=scrollbar.set)
        
        # TreeviewとScrollbarの配置
        self.weather_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # イベントの設定
        self.load_prefectures()
        self.prefecture_combo.bind('<<ComboboxSelected>>', self.on_prefecture_select)
        self.city_combo.bind('<<ComboboxSelected>>', self.on_city_select)

    def load_prefectures(self):
        # 都道府県データの読み込み
        self.cursor.execute("SELECT prefecture_code, prefecture_name FROM prefectures")
        prefectures = self.cursor.fetchall()
        self.prefecture_combo['values'] = [pref[1] for pref in prefectures]
    
    def on_prefecture_select(self, event):
        # 選択された都道府県の市区町村を読み込む
        selected_prefecture = self.prefecture_var.get()
        self.cursor.execute("""
            SELECT c.city_code, c.city_name 
            FROM cities c
            JOIN prefectures p ON c.prefecture_code = p.prefecture_code
            WHERE p.prefecture_name = ?
        """, (selected_prefecture,))
        cities = self.cursor.fetchall()
        self.city_combo['values'] = [city[1] for city in cities]
        self.city_combo.set('')  # 市区町村の選択をクリア

    def on_city_select(self, event):
        self.update_weather()

    def update_weather(self):
        # Treeviewのクリア
        for item in self.weather_tree.get_children():
            self.weather_tree.delete(item)
        
        # 選択された市区町村のコードを取得
        selected_city = self.city_var.get()
        if not selected_city:
            return
            
        self.cursor.execute("""
            SELECT city_code 
            FROM cities 
            WHERE city_name = ?
        """, (selected_city,))
        city_code = self.cursor.fetchone()
        
        if city_code:
            # 天気情報の取得と表示
            self.cursor.execute("""
                SELECT forecast_target_date, weather_text, 
                       temperature_max, temperature_min, 
                       precipitation_probability
                FROM weather_forecasts
                WHERE area_code = ?
                ORDER BY forecast_target_date
            """, (city_code[0],))
            
            for row in self.cursor.fetchall():
                self.weather_tree.insert("", "end", values=row)

def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()