import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import requests
import concurrent.futures
import threading
from bs4 import BeautifulSoup
import os
import csv

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

OUTPUT_PATH = os.path.join('./results/')

def get_news_df(ticker_url, ticker, writer):
    r = requests.get(ticker_url)
    root = ET.fromstring(r.text)
    for item in root.iter('item'):
        title = item.find('title').text
        link = item.find('link').text
        author = item.find('author').text
        author = author.replace('(', '').replace(')', '')
        description = item.find('description').text
        pub_date = item.find('pubDate').text
        news = [ ticker, title, description, pub_date, link, author ]
        writer.writerow(news)
        print(f"SUCCESSFUL NEWS EXTRACTION [{ticker}]: {link}")

# This method is a little slow for parsing the web
# but since there's embedded code in the paragraphs, svg, and other elements,
# it would be a nightmare to parse trough a custom method
def get_accurate_description(row, writer):
    description = ''
    r = requests.get(row['link'], headers=HEADERS)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find('div', class_='caas-body')
    if content:
        for p in content.find_all('p'):
            p_text = p.string if p.string != None else ''
            description += p_text
        row['pub_date'] = soup.find('time').string if soup.find('time') else ''
        row['description'] = bytes(description, 'utf-8').decode('utf-8', 'ignore')
    print(f"SUCCESSFUL DESCRIPTION EXCTRACTION [{row['ticker']}]: {row['link']}")
    writer.writerow(row.to_list())

def write_header(writer):
    header = ['ticker', 'title', 'description', 'pub_date', 'link', 'author'] 
    writer.writerow(header)

def get_news_driver(output_path):
    output_path_file = os.path.join(output_path, "output.csv")
    with open(output_path_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        write_header(writer)
        with concurrent.futures.ThreadPoolExecutor(4) as executor:
            for ticker in TICKERS:
                ticker_url = FINVIZ + ticker
                executor.submit(get_news_df, ticker_url, ticker, writer)

def get_description_driver(output_path):
    output_path_file = os.path.join(output_path, "output.csv")
    output_path_file_des = os.path.join(output_path, "output_des.csv")
    df = pd.read_csv(output_path_file)
    with open(output_path_file_des, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        write_header(writer)
        with concurrent.futures.ThreadPoolExecutor(4) as executor:
            for _, row in df.iterrows():
                executor.submit(get_accurate_description, row, writer)

def get_news(output_path = None):
    if output_path:
        get_news_driver(output_path)
        get_description_driver(output_path)
    else:
        get_news_driver(OUTPUT_PATH)
        get_description_driver(OUTPUT_PATH)

if __name__ == '__main__':
    get_news()