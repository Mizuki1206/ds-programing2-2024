import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sqlite3
from datetime import datetime

class PopulationScraper:
    def __init__(self):
        self.url = "https://uub.jp/pjn/pb.html"
    
    def validate_data(self, df):
        """データの基本的な検証を行う"""
        validations = {
            'データ数の確認': len(df) == 47,
            '必須列の存在': all(col in df.columns for col in ['prefecture', 'population', 'area', 'density']),
            'NULL値の確認': not df.isnull().any().any(),
            '人口の範囲': (df['population'] > 0).all(),
            '面積の範囲': (df['area'] > 0).all(),
            '密度の範囲': (df['density'] > 0).all()
        }
        
        all_valid = all(validations.values())
        if not all_valid:
            print("\n検証結果:")
            for check, result in validations.items():
                print(f"{check}: {'OK' if result else 'NG'}")
        
        return all_valid

    def fetch_data(self):
        """Webサイトから人口統計データを取得する"""
        time.sleep(1)
        
        try:
            response = requests.get(self.url)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            data = []
            table = soup.find('table')
            rows = table.find_all('tr')

            # ヘッダー行をスキップ
            for row in rows[1:]:
                cols = row.find_all('td')
                # 必要な列数があることを確認
                if len(cols) >= 7:
                    data.append({
                        'prefecture': cols[0].text.strip(),
                        'prefecture_kana': cols[1].text.strip(),
                        'city': cols[2].text.strip(),
                        'city_kana': cols[3].text.strip(),
                        'population': int(cols[4].text.strip().replace(',', '')),
                        'area': float(cols[5].text.strip().replace(',', '')),
                        'density': float(cols[6].text.strip().replace(',', '')),
                        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            df = pd.DataFrame(data)
            return df
        
        except Exception as e:
            print(f"データの取得中にエラーが発生しました: {str(e)}")
            return None
            
    def save_to_db(self, df):
        """DataFrameをSQLiteデータベースに保存"""
        if df is None or df.empty:
            print("保存するデータがありません")
            return False
        
        try:
            conn = sqlite3.connect('traffic_data.db')
            df.to_sql('population_data', conn, if_exists='replace', index=False)
            conn.close()
            print("データベースへの保存が完了しました")
            return True
        except Exception as e:
            print(f"データベース保存中にエラーが発生: {str(e)}")
            return False

    def run(self):
        """スクレイピングの実行とデータ保存を行う"""
        df = self.fetch_data()
        if df is not None and self.validate_data(df):
            if self.save_to_db(df):
                return df
        return None

if __name__ == "__main__":
    scraper = PopulationScraper()
    df = scraper.run()
    
    if df is not None:
        print("\nデータのプレビュー:")
        print(df.head())
        print(f"\n取得したデータ数: {len(df)}行")
        
        # 基本的な統計情報の表示
        print("\n基本統計情報:")
        print(f"総人口: {df['population'].sum():,}人")
        print(f"平均人口密度: {df['density'].mean():.2f}人/km2")
        print(f"最も人口が多い都道府県: {df.loc[df['population'].idxmax(), 'prefecture']}")
        print(f"最も人口密度が高い都道府県: {df.loc[df['density'].idxmax(), 'prefecture']}")