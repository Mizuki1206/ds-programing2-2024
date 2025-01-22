import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class TrafficAnalyzer:
    def __init__(self):
        self.db_path = 'traffic_data.db'
        
    def clean_accident_data(self, df):
        """交通事故データのクリーニング"""
        try:
            total_rows = []
            print("\n=== データ読み込み開始 ===")

            # DataFrameのコピーを作成
            df = df.copy()

            # 必要な列だけを選択
            columns_needed = ['地域コード', '管区・支局', '都道府県・方面本部', '件', '人', '人.1']
            df = df[columns_needed]

            # 地域コードを数値に変換（欠損値はNaNに）
            df['地域コード'] = pd.to_numeric(df['地域コード'], errors='coerce')

            # 都道府県データを抽出
            # まず地域コード1-47の都道府県を抽出
            prefecture_data = df[
                (df['地域コード'].between(1, 47)) & 
                (df['都道府県・方面本部'] != '計')
            ].copy()

            # 北海道の合計行を取得
            hokkaido_total = df[
                (df['管区・支局'] == '北海道') & 
                (df['都道府県・方面本部'] == '計')
            ].copy()

            # 北海道のデータを追加
            if not hokkaido_total.empty:
                prefecture_data = pd.concat([hokkaido_total, prefecture_data])

            print(f"抽出された都道府県数: {len(prefecture_data)}")

            # 各都道府県のデータを処理
            for _, row in prefecture_data.iterrows():
                # 都道府県名の取得部分を修正
                prefecture = str(row['都道府県・方面本部']).strip()
                if prefecture == '計':
                    prefecture = str(row['管区・支局']).strip()  # 北海道の場合のみ

            
                try:
                    # floatに変換してからintに変換
                    accidents = int(float(str(row['件']).replace('"', '').replace(',', '')))
                    deaths = int(float(str(row['人']).replace('"', '').replace(',', '')))
                    injuries = int(float(str(row['人.1']).replace('"', '').replace(',', '')))
                
                    print(f"抽出データ: {prefecture} - 事故:{accidents}, 死者:{deaths}, 負傷:{injuries}")
                
                    total_rows.append({
                        'prefecture': prefecture,
                        'accidents': accidents,
                        'deaths': deaths,
                        'injuries': injuries
                    })
                except ValueError as e:
                    print(f"警告: {prefecture}のデータ変換中にエラー: {str(e)}")
                    continue

            cleaned_df = pd.DataFrame(total_rows)
            return cleaned_df

        except Exception as e:
            print(f"データクリーニング中にエラー: {str(e)}")
            return None

    def load_data(self):
        """データベースと事故データのCSVを読み込み、結合する"""
        try:
            print("CSVファイル読み込み開始...")
        
            # 交通事故データの読み込み
            accident_df = pd.read_csv('表4-1.csv', 
                                    encoding='shift_jis', 
                                    skiprows=3,  
                                    thousands=',',  
                                    na_values=['***'])
        
            print(f"読み込んだCSVの行数: {len(accident_df)}")
            print("カラム名:", accident_df.columns.tolist())
        
            # データクリーニング
            accident_df = self.clean_accident_data(accident_df)
        
            if accident_df is not None and not accident_df.empty:
                print("\n=== クリーニング後の交通事故データ ===")
                print(accident_df.head())
                print("\n交通事故データの基本統計量:")
                print(accident_df.describe())
                print("\n交通事故データ件数:", len(accident_df))
            
                # SQLiteデータベースから人口データを読み込む
                try:
                    conn = sqlite3.connect(self.db_path)
                    population_df = pd.read_sql_query(
                        "SELECT prefecture, population, density FROM population_data",
                        conn
                    )
                    conn.close()
                
                    print("\n=== 人口データ ===")
                    print(population_df.head())
                    print("\n人口データ件数:", len(population_df))
                
                    return accident_df, population_df
                
                except Exception as e:
                    print(f"人口データの読み込み中にエラー: {str(e)}")
                    return None, None
            
            return None, None
    
        except Exception as e:
            print(f"データ読み込み中にエラー: {str(e)}")
            return None, None

    def merge_data(self, accident_df, population_df):
        """データの結合と分析用データの作成"""
        try:
            if accident_df is None or population_df is None:
                print("データ結合エラー: 入力データが不正です")
                return None

            # データフレームのコピーを作成
            accident_df = accident_df.copy()
            population_df = population_df.copy()

            # 都道府県名を統一（事故データ側）
            special_prefectures = {
                '北海道': '北海道',
                '東京': '東京都',
                '京都': '京都府',
                '大阪': '大阪府'
            }
        
            # 都道府県名の変換関数
            def convert_prefecture_name(name):
                if name in special_prefectures:
                    return special_prefectures[name]
                return name + '県'
        
            # 都道府県名を変換
            accident_df['prefecture'] = accident_df['prefecture'].apply(convert_prefecture_name)

            print("\n=== 変換後のデータ確認 ===")
            print("事故データの都道府県名サンプル:", accident_df['prefecture'].head().tolist())
        
            # データを結合
            merged_df = pd.merge(
                accident_df,
                population_df,
                on='prefecture',
                how='inner'
            )

            # 必要な列のみを選択
            columns_to_keep = ['prefecture', 'accidents', 'deaths', 'injuries', 
                            'population', 'density']
            merged_df = merged_df[columns_to_keep]

            # 人口10万人あたりの事故率を計算
            merged_df['accident_rate'] = (merged_df['accidents'] / merged_df['population']) * 100000
            merged_df['death_rate'] = (merged_df['deaths'] / merged_df['population']) * 100000
            merged_df['injury_rate'] = (merged_df['injuries'] / merged_df['population']) * 100000

            print("\n=== 結合後のデータ概要 ===")
            print(merged_df.head())
            print(f"\n合計データ数: {len(merged_df)}件")

            # 基本的な分析結果を表示
            print("\n=== 基本統計情報 ===")
            print(f"平均事故発生率（10万人あたり）: {merged_df['accident_rate'].mean():.2f}件")
            print(f"平均死亡率（10万人あたり）: {merged_df['death_rate'].mean():.2f}人")
            print(f"人口密度と事故率の相関係数: {merged_df['density'].corr(merged_df['accident_rate']):.3f}")

            return merged_df

        except Exception as e:
            print(f"データ結合中にエラーが発生: {str(e)}")
            return None

if __name__ == "__main__":
    analyzer = TrafficAnalyzer()
    
    # データの読み込みと処理を実行
    print("=== データ分析開始 ===")
    result = analyzer.load_data()
    
    if result is not None:
        accident_df, population_df = result
        # データの結合
        merged_data = analyzer.merge_data(accident_df, population_df)
        if merged_data is not None:
            print("\n=== 分析完了 ===")
    else:
        print("データの読み込みに失敗しました")