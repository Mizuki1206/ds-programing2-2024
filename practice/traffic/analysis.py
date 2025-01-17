import pandas as pd
import sqlite3
from typing import Dict, List
import re

class TrafficDataProcessor:
    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        
    def clean_numeric(self, value: str) -> float:
        """数値データのクリーニング"""
        if pd.isna(value):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        
        # カンマと*を除去
        value = str(value).replace(',', '').replace('*', '')
        # 数値以外を除去
        value = re.sub(r'[^0-9.-]', '', value)
        
        try:
            return float(value) if value else None
        except ValueError:
            return None

    def load_traffic_data(self) -> pd.DataFrame:
        """交通事故データの読み込みとクリーニング"""
        try:
            # CSVファイルの読み込み（shift-jisエンコーディングを使用）
            df = pd.read_csv(self.csv_file, encoding='shift-jis', skiprows=3)
            
            # 列名を設定
            df.columns = ['地域コード', '管区・支局', '都道府県', 
                         '事故件数', '事故増減数', '事故増減率',
                         '死者数', '死者増減数', '死者増減率', '死者順位',
                         '負傷者数', '負傷者増減数', '負傷者増減率']
            
            # 計や合計の行を除外
            df = df[~df['都道府県'].str.contains('計|合計', na=False)]
            
            # 必要な列の選択
            df_cleaned = df[['都道府県', '事故件数', '死者数', '負傷者数']].copy()
            
            # 数値データのクリーニング
            numeric_columns = ['事故件数', '死者数', '負傷者数']
            for col in numeric_columns:
                df_cleaned[col] = df_cleaned[col].apply(self.clean_numeric)
            
            # 列名を英語に変更
            columns_rename = {
                '都道府県': 'prefecture',
                '事故件数': 'accidents',
                '死者数': 'deaths',
                '負傷者数': 'injuries'
            }
            
            return df_cleaned.rename(columns=columns_rename)
            
        except Exception as e:
            print(f"データ読み込み中にエラーが発生: {str(e)}")
            raise

    def save_to_db(self, df: pd.DataFrame, table_name: str):
        """データをSQLiteデータベースに保存"""
        conn = sqlite3.connect('traffic_data.db')
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()

def main():
    # データ処理インスタンスの作成
    processor = TrafficDataProcessor('表4-1.csv')
    
    try:
        # データの読み込みとクリーニング
        df = processor.load_traffic_data()
        
        # 基本的な統計情報の表示
        print("\nデータの最初の5行:")
        print(df.head())
        
        print("\nデータサマリー:")
        print(df.describe())
        
        # データベースへの保存
        processor.save_to_db(df, 'traffic_accidents')
        print("\nデータベースへの保存が完了しました")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()