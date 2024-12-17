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
        self.prefecture_var = tk.StringVar()
        self.prefecture_combo = ttk.Combobox(
            self.area_frame, 
            textvariable=self.prefecture_var,
            state='readonly'
        )
        self.prefecture_combo.pack(side="left", padx=5)
        
        # 市区町村選択
        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(
            self.area_frame, 
            textvariable=self.city_var,
            state='readonly'
        )
        self.city_combo.pack(side="left", padx=5)
        
        # 天気情報表示フレーム
        self.weather_frame = ttk.LabelFrame(self.root, text="天気情報", padding=10)
        self.weather_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 天気情報を表示するTreeview
        self.weather_tree = ttk.Treeview(self.weather_frame, columns=(
            "日付", "天気", "気温", "降水確率"
        ))
        self.weather_tree.heading("日付", text="日付")
        self.weather_tree.heading("天気", text="天気")
        self.weather_tree.heading("気温", text="気温")
        self.weather_tree.heading("降水確率", text="降水確率")
        self.weather_tree.pack(fill="both", expand=True)
        
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

    def on_city_select(self, event):
        # 選択された市区町村の天気情報を表示
        pass

def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()