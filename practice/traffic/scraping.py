import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sqlite3
from pathlib import Path

class TrafficDataScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.db_path = Path("traffic.db")

    def get_estat_traffic_data(self):
        """e-Statから交通事故データを取得"""
        url = "https://www.e-stat.go.jp/stat-search/files"
        params = {
            'page': '1',
            'layout': 'datalist',
            'toukei': '00130002',
            'tstat': '000001032727',
            'cycle': '1',
            'year': '20240',
            'month': '24101211',
            'tclass1val': '0'
        }

        try:
            print("Accessing e-stat website...")
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            print("\nChecking HTML content...")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # ページの構造を確認
            print("\nPage structure:")
            print("Title:", soup.title.string if soup.title else "No title found")
            
            # すべてのdivを確認
            divs = soup.find_all('div')
            print(f"\nFound {len(divs)} divs")
            
            # すべてのリンクを確認
            links = soup.find_all('a')
            print(f"\nFound {len(links)} links")
            print("\nChecking links containing 'CSV':")
            for link in links:
                if 'CSV' in str(link):
                    print(f"Link text: {link.text.strip()}")
                    print(f"Link href: {link.get('href')}")
                    print("Link class:", link.get('class', 'No class'))
                    print()

            return None

        except Exception as e:
            print(f"\nError during scraping: {e}")
            return None

def main():
    scraper = TrafficDataScraper()
    print("Starting data collection...")
    scraper.get_estat_traffic_data()
    print("\nData collection process finished")

if __name__ == "__main__":
    main()