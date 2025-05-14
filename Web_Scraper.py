# importing dependencies 
import pandas as pd
import numpy as np
import json
import selenium
from selenium import webdriver
from datetime import date as d
import boto3
from decimal import Decimal


class ArticleScraper():
    
    def __init__(self):
        #load in csv 
        self.companies = pd.read_csv('combined_function_inputs.csv')
        print(self.companies.head())

    def get_dataframe(self):
        return self.companies


    def scrape(
        self, start_url, get_urls, get_title, get_body, cookie=None, get_meta=None, get_date=None
    ):
        
        driver = webdriver.Chrome()
        driver.implicitly_wait(10) 
        records = []
        # Navigate to webpage, and click yes for cookies
        driver.get(start_url)
        # cookies
        if isinstance(cookie, str):
            try:
                driver.find_element('xpath', cookie).click()
            except Exception as e:
                print(f"CookieError: {e}, Website: {start_url}")


        # Find all of the anchor tags on the webpage
        links = driver.find_elements('xpath', get_urls)


        # Extract the URLs from the anchor tags
        urls = [link.get_attribute("href") for link in links]

        # Print the URLs if you'd like
    #     print(urls)

        # scraping body text and title

        for url in urls:
            # need to do this. (check url, if there, ignore it)
            if url is None:
                continue
            try:
                driver.get(url)
                record = {'url': url}
            except selenium.common.exceptions.TimeoutException as e:
                print(e)
                continue
            
            try:
                title = driver.find_element('xpath',get_title).get_attribute('innerText')
                record['title'] = title
            except selenium.common.exceptions.NoSuchElementException as e:
                print(e)
                continue
            
            try:
                body = driver.find_element('xpath', get_body).get_attribute('innerText')
                record['body'] = body
            except:
                pass
                
            if isinstance(get_meta, str):
                try:
                    description = driver.find_element('xpath', get_meta).get_attribute('innerText')
                    record['description'] = description
                except Exception as e:
                    print(f"GetDescriptionError: {e}, URL: {url}")
            else:
                description = None

                
            records.append(record) 
        #changing articles to json    
        # scraped_articles = json.dumps(records, indent=4)  
    #         print(title)
        return records, driver

        #rows = df.iloc[37:,:]

    def get_articles(self, companies):
        #initializing dictionary to hold all articles
        company_articles = {}
        #going through every single company
        for index, row in companies.iterrows():
            # going through to get all the information
            all_articles, driver = self.scrape(row['start_URL'], row['get_urls'], 
                                                            row['get_title'], row['get_body'], 
                                                            row['cookie'], row['get_meta'], row['get_date'])
            
            scraped_articles = {}
            for i in range(len(all_articles)):
                scraped_articles[i] = all_articles[i]
            print(type(scraped_articles))

            #adding in company name to each article
            company_name = row['company']
            i = 1
            publish_date = []
            for key in scraped_articles:
                article = scraped_articles[key]
                print(article)
                #checking to see if the article has a date
                if 'date' not in article:
                    #checking to see if we need a starter date
                    if i == 1:
                        #setting default first date so that the date will be easy to find next time
                        date = d.today()
                    else:
                        #keep the dates more or less how they should be if there aren't dates
                        date = publish_date[-1]
                    i += 1

                if 'description' not in article:
                    #checking to see if there is no description
                    article['description'] = None

                if 'title' not in article:
                    #checking to see if there is no description
                    article['title'] = None   

                if 'body' not in article:
                    #checking to see if there is no description
                    article['title'] = None                                  
                
                article_date = date
                article['date'] = article_date
            
                publish_date.append(article_date)
                article_url = article['url']
                article['company_name'] = company_name
                
                #creating a unique articleID
                article_ID = company_name + "_" + article_url 
                #adding articleID to the dictionary of articles
                article['article_id'] = article_ID

                self.insert_article(article)

                #adding the whole json to a dictionary that we will use to insert everything into.
                company_articles[article_ID] = article
        
        self.quit_driver(driver)
        return company_articles

    def insert_article(self, article):
        # Get the service resource.
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('TEST_TABLE')
        #print(table.creation_date_time)
        
        #article unique id
        article_ID = str(article['article_id'])
        print(article_ID)
        #making sure we have the company name
        company_name = str(article['company_name'])
        #article title
        article_title = str(article['title'])
        #url
        article_url = str(article['url'])
        #metat description
        article_description = str(article['description'])
        #date the article was written
        article_date = str(article['date'])
        #the body of the article
        article_body = str(article['body'])

        with table.batch_writer(overwrite_by_pkeys=['article_id']) as batch:
            batch.put_item(
                Item={
                    'article_id': article_ID,
                    'article_date': article_date,
                    'article_url': article_url,
                    'company_name': company_name,
                    'article_title': article_title,
                    'article_descirption': article_description,
                    'article_body': article_body,  
                }
            )

    def quit_driver(self, driver):
        # Close the browser
        driver.quit()   

def Main():
    company_articles = ArticleScraper()
    companies = company_articles.get_dataframe()
    articles = company_articles.get_articles(companies)
    print(articles)

Main()           