import pandas as pd
import numpy as np

# CSVファイルを読み込む
df = pd.read_csv('表4-1.csv', encoding='cp932')

# すべての列の値を確認
print("=== 各列のデータ ===")
for col in df.columns:
    print(f"\n列名: {col}")
    print(df[col].head(15))  # 最初の15行を表示

print("\n=== データの形状 ===")
print(f"行数: {df.shape[0]}, 列数: {df.shape[1]}")

# 数値として解釈できる可能性のある列を確認
print("\n=== 数値データの確認 ===")
for col in df.columns:
    try:
        # 数値に変換を試みる
        numeric_values = pd.to_numeric(df[col], errors='coerce')
        non_null_count = numeric_values.notna().sum()
        if non_null_count > 0:
            print(f"\n列 {col} の数値データ数: {non_null_count}")
            print("サンプル値:")
            print(numeric_values[numeric_values.notna()].head())
    except:
        continue