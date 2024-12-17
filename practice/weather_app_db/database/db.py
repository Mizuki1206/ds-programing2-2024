import sqlite3
import json
from pathlib import Path

def init_db():
    conn = sqlite3.connect('weather_app.db')
    c = conn.cursor()

    # 地方テーブル
    c.execute('''CREATE TABLE IF NOT EXISTS regions
                 (region_code TEXT PRIMARY KEY, region_name TEXT NOT NULL, 
              region_en_name TEXT, office_name TEXT)''')
    
    # 地域・県テーブル
    c.execute('''CREATE TABLE IF NOT EXISTS prefectures
                 (prefecture_code TEXT PRIMARY KEY, prefecture_name TEXT NOT NULL, 
              prefecture_en_name TEXT, region_code TEXT, office_name TEXT, 
                FOREIGN KEY(region_code) REFERENCES regions(region_code))''')
    
    # 市区町村テーブル
    c.execute('''CREATE TABLE IF NOT EXISTS cities
                 (city_code TEXT PRIMARY KEY, city_name TEXT NOT NULL, 
              city_en_name TEXT, city_kana TEXT, prefecture_code TEXT, 
                FOREIGN KEY(prefecture_code) REFERENCES prefectures(prefecture_code))''')
    
    # 天気予報テーブル
    c.execute('''CREATE TABLE IF NOT EXISTS weather_forecasts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, area_code TEXT NOT NULL, 
              forecasst_target_data TEXT NOT NULL, forecast_publish_time TEXT NOT NULL, 
              weather_code TEXT, weather_text TEXT, temperature_min INTEGER, 
                temperature_max INTEGER, temperature_min_upper INTEGER, 
              temperature_min_lower INTEGER, temperature_max_upper INTEGER, 
                temperature_max_lower INTEGER, precipitation_probability INTEGER, 
              reliability TEXT, wind_text TEXT, wave_text TEXT, 
              created_at TEXT NOT NULL)''')
    
    conn.commit()
    return conn

def load_area_data():
    with open('area.json', 'r', encoding='utf-8') as f:
        area_data = json.load(f)
        conn = init_db()
        cursor = conn.cursor()

        # centersデータの保存
        for code, data in area_data['centers'].items():
            cursor.execute('''INSERT OR REPLACE INTO regions(region_code, region_name, region_en_name, office_name)
                                VALUES(?, ?, ?, ?)''', (code, data['name'], data['enName'], data['officeName']))
            
        # officesデータの保存
        for code, data in area_data['offices'].items():
            cursor.execute('''INSERT OR REPLACE INTO prefectures(prefecture_code, prefecture_name, prefecture_en_name, region_code, office_name)
                                VALUES(?, ?, ?, ?, ?)''', (code, data['name'], data['enName'], data.get('parent'), data['officeName']))
            
        # class20sデータの保存
        for code, data in area_data['class20s'].items():
            cursor.execute('''INSERT OR REPLACE INTO cities(city_code, city_name, city_en_name, city_kana, prefecture_code)
                                VALUES(?, ?, ?, ?, ?)''', (code, data['name'], data['enName'], data['kana'], data.get('parent')))
            
        conn.commit()
        return conn
    
if __name__ == '__main__':
    load_area_data()