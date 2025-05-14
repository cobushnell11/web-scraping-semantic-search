# importing dependencies 

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import json

df2 = pd.read_excel('C:\\Users\\cobus\\OneDrive\\Documents\\ASPIRE\\lxml_inputs.xlsx')


import selenium
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(10)


from lxml import html

def special_scrape(
    start_url, get_cookie, get_entry, get_title, get_date, get_url, get_summary
    
):
    
    records = []
    # Navigate to webpage, and click yes for cookies
    try:
        driver.get(start_url)
    except selenium.common.exceptions.TimeoutException as e:
        print(e)
        return records
    # cookies
    if isinstance(get_cookie, str):
        try:
            driver.find_element('xpath', get_cookie).click()
        except Exception as e:
            print(f"CookieError: {e}, Website: {start_url}")


    # Find all entries
    entries = driver.find_elements('xpath',get_entry)
    

    # scraping body text and title for each article
    for entry in entries:
        tree = html.fromstring(entry.get_attribute('innerHTML'))
        record = {}
        try:
            title = tree.xpath(get_title)[0].text
            record['title']= title
            url = tree.xpath(get_url)[0].attrib['href']
            record['url']= url
        except:
            print('error')
            continue
        try:
            date = tree.xpath(get_date)[0].text
            record['date']= date
        except:
            pass 
        try:
            summary = tree.xpath(get_summary)[0].text
            record['summary']= summary
        except:
            pass 
    
    
            
        records.append(record)
#         print(title)
    return records



for index, row in df2.iterrows():
    # right here
    print(row['company'])
    scraped_articles = special_scrape(row['start_url'], row['get_cookie'], row['get_entry'], row['get_title'], row['get_date'],row['get_url'], row['get_summary'])
    
    print(json.dumps(scraped_articles))
