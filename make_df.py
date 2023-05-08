import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import requests
import concurrent.futures
import threading
from bs4 import BeautifulSoup
import os

thread_local = threading.local()

HOST = "http://localhost:1200"
# We need to add the stock ticker its specific news
FINVIZ = HOST + "/finviz/news/"
TEST_TICKER = FINVIZ + "AAPL"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36', 
    'Accept-Language': 'en-US,en;q=0.5', 
    'Accept-Encoding': 'gzip, deflate, br'
}

TICKERS = [
    'AAPL', 'MSFT', 'GOOG', 'AMZN', 'NVDA', 'META',
    'TSLA', 'BABA', 'CRM', 'AMD', 'INTC', 'PYPL',
    'ATVI', 'EA', 'TTD', 'ZG', 'MTCH', 'YELP',
]

def get_news_df(ticker_url):
    news_dict = []
    r = requests.get(ticker_url)
    root = ET.fromstring(r.text)
    for item in root.iter('item'):
        title = item.find('title').text
        description = item.find('description').text
        pub_date = None
        link = item.find('link').text
        author = item.find('author').text
        author = author.replace('(', '').replace(')', '')
        news = {
            'title': title, 
            'description': description,
            'pub_date':pub_date,
            'link':link,
            'author':author,
        }
        news_dict.append(news)
    return pd.DataFrame(data=news_dict)

# This method is a little slow for parsing the web
# but since there's embedded code in the paragraphs, svg, and other elements,
# it would be a nightmare to parse trough a custom method
def get_accurate_description(df, ticker):
    links = df['link']
    for index, row in df.iterrows():
        description = ''
        r = requests.get(row['link'], headers=HEADERS)
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        content = soup.find('div', class_='caas-body')
        if content:
            df.at[index, 'pub_date'] = soup.find('time').string if soup.find('time') else ''
            for p in content.find_all('p'):
                p_text = p.string if p.string != None else ''
                description += p_text
            df.at[index, 'description'] = description
    path = os.path.join('./results/', ticker + '.csv')
    df.to_csv(path, index=False)


def driver():
    for ticker in TICKERS:
        df = get_news_df(FINVIZ + ticker)
        get_accurate_description(df, ticker)

if __name__ == '__main__':
    driver()