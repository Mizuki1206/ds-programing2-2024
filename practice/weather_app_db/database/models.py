from datetime import datetime

class WeatherData:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()

    def save_forecast(self, data, area_code):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for timeSeries in data[0]['timeSeries']:
            for area in timeSeries['areas']:
                # timeDefinesとデータを紐付けて保存
                for i, time in enumerate(timeSeries['timeDefines']):
                    weather = area.get('weathers', [''])[i] if 'weathers' in area else None
                    weather_code = area.get('weatherCodes', [''])[i] if 'weatherCodes' in area else None
                    temp = area.get('temps', [''])[i] if 'temps' in area else None
                    
                    self.cursor.execute('''
                    INSERT INTO weather_forecasts 
                    (area_code, forecast_target_date, forecast_publish_time, 
                     weather_code, weather_text, temperature_max, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (area['area']['code'], time, data[0]['reportDatetime'],
                          weather_code, weather, temp, now))
        
        self.conn.commit()

    def get_forecast(self, area_code):
        self.cursor.execute('''
        SELECT * FROM weather_forecasts 
        WHERE area_code = ? 
        ORDER BY forecast_target_date DESC 
        LIMIT 10
        ''', (area_code,))
        return self.cursor.fetchall()