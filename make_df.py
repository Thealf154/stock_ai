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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        + 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36', 
    'Accept-Language': 'en-US,en;q=0.5', 
    'Accept-Encoding': 'gzip, deflate, br'
}

TICKERS = [
    'AAPL', 'MSFT', 'GOOG', 'AMZN', 'NVDA', 'META',
    'TSLA', 'BABA', 'CRM', 'AMD', 'INTC', 'PYPL',
    'ATVI', 'EA', 'TTD', 'ZG', 'MTCH', 'YELP',
]

OUTPUT_PATH = os.path.join('./results/', 'output' + '.csv')

def get_news_df(ticker_url, ticker):
    news_dict = []
    r = requests.get(ticker_url)
    root = ET.fromstring(r.text)
    for item in root.iter('item'):
        title = item.find('title').text
        link = item.find('link').text
        author = item.find('author').text
        author = author.replace('(', '').replace(')', '')
        description, pub_date = get_accurate_description(link)
        news = {
            'ticker': ticker,
            'title': title, 
            'description': description,
            'pub_date':pub_date,
            'link':link,
            'author':author
        }
        news_dict.append(news)
    pd.DataFrame(data=news_dict).to_csv(OUTPUT_PATH, mode='a', index=False)

# This method is a little slow for parsing the web
# but since there's embedded code in the paragraphs, svg, and other elements,
# it would be a nightmare to parse trough a custom method
def get_accurate_description(link):
    description = ''
    pub_date = ''
    r = requests.get(link, headers=HEADERS)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find('div', class_='caas-body')
    if content:
        pub_date = soup.find('time').string if soup.find('time') else ''
        for p in content.find_all('p'):
            p_text = p.string if p.string != None else ''
            description += p_text
        description = description
    return description, pub_date

def get_news_driver():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for ticker in TICKERS:
            ticker_url = FINVIZ + ticker
            executor.submit(get_news_df, ticker_url, ticker)

def main():
    get_news_driver()

if __name__ == '__main__':
    main()